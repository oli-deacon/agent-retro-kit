#!/usr/bin/env bash
# auto-log.sh — called by Claude Code Stop hook.
# Finds the most recent session JSONL for the current project,
# extracts metadata via Haiku, appends a row to run-log.csv,
# then prompts for the 2 human-review fields.
set -euo pipefail

KIT_DIR="$HOME/agent-retro-kit"
RUN_LOG="$KIT_DIR/data/run-log.csv"
EXTRACTOR="$KIT_DIR/scripts/extract-run-metadata.py"
PROJECTS_DIR="$HOME/.claude/projects"

# Derive the project slug from CWD (same convention Claude Code uses)
cwd_slug=$(pwd | sed 's|/|-|g' | sed 's|^-||')
project_dir="$PROJECTS_DIR/$cwd_slug"

if [ ! -d "$project_dir" ]; then
  echo "[auto-log] No Claude project dir for $cwd_slug — skipping" >&2
  exit 0
fi

# Find the most recently modified JSONL
session_file=$(ls -t "$project_dir"/*.jsonl 2>/dev/null | head -1)

if [ -z "$session_file" ]; then
  echo "[auto-log] No session files found — skipping" >&2
  exit 0
fi

# Check minimum size (skip trivially short sessions < 5 lines)
line_count=$(wc -l < "$session_file")
if [ "$line_count" -lt 5 ]; then
  echo "[auto-log] Session too short ($line_count lines) — skipping" >&2
  exit 0
fi

# Check if this session was already logged (dedup by session_ref)
session_id=$(basename "$session_file" .jsonl)
if grep -q "$session_id" "$RUN_LOG" 2>/dev/null; then
  echo "[auto-log] Session $session_id already logged — skipping" >&2
  exit 0
fi

echo "[auto-log] Extracting metadata from $session_file ..."

# Run extractor — capture JSON output
metadata=$(python3 "$EXTRACTOR" "$session_file") || {
  echo "[auto-log] Extraction failed — skipping" >&2
  exit 0
}

# Parse fields from JSON
get() { echo "$metadata" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null; }

task_title=$(get task_title)
outcome=$(get outcome_inferred)
needs_review=$(get needs_review)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Agent Retro — Log this session"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Task:    $task_title"
echo "  Outcome: $outcome"
echo ""

# 2 human-review prompts (the only fields Haiku can't know)
read -r -p "  Accepted without edit? [yes/no/uncertain, Enter=uncertain]: " accepted
accepted="${accepted:-uncertain}"

read -r -p "  Verification status? [completed/blocked/not_needed/uncertain, Enter=uncertain]: " verification
verification="${verification:-uncertain}"

echo ""

# Build the CSV row
run_id="$(date +%Y-%m-%d)-$(( $(grep -c ',' "$RUN_LOG" 2>/dev/null || echo 0) ))"
captured_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
model=$(python3 -c "import json,pathlib; s=pathlib.Path('$HOME/.claude/settings.json').read_text(); d=json.loads(s); print(d.get('model','claude-sonnet-4-6'))" 2>/dev/null || echo "claude-sonnet-4-6")

# Escape a field for CSV (wrap in quotes, escape internal quotes)
csv_field() {
  local val="$1"
  val="${val//\"/\"\"}"
  echo "\"$val\""
}

row=$(printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
  "$(csv_field "$run_id")" \
  "$(csv_field "$captured_at")" \
  "$(csv_field "$(get project)")" \
  "$(csv_field "$(get workspace_path)")" \
  "$(csv_field "claude_code")" \
  "$(csv_field "$model")" \
  "$(csv_field "$(get session_ref)")" \
  "$(csv_field "")" \
  "$(csv_field "$task_title")" \
  "$(csv_field "$(get run_started_at)")" \
  "$(csv_field "$(get run_last_updated_at)")" \
  "$(csv_field "$(get duration_minutes_inferred)")" \
  "$(csv_field "$(get user_prompt_summary)")" \
  "$(csv_field "$(get task_type_inferred)")" \
  "$(csv_field "$(get outcome_inferred)")" \
  "$(csv_field "$(get accepted_without_edit_inferred)")" \
  "$(csv_field "$(get retry_count_inferred)")" \
  "$(csv_field "$(get error_summary_inferred)")" \
  "$(csv_field "$(get tool_summary)")" \
  "$(csv_field "$(get coding_intensity)")" \
  "$(csv_field "$needs_review")" \
  "$(csv_field "$(get sampling_reason)")" \
  "$(csv_field "")" \
  "$(csv_field "$accepted")" \
  "$(csv_field "")" \
  "$(csv_field "")" \
  "$(csv_field "")" \
  "$(csv_field "")" \
  "$(csv_field "$verification")" \
  "$(csv_field "")" \
  "$(csv_field "")")

echo "$row" >> "$RUN_LOG"
echo "  ✓ Logged to run-log.csv"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
