#!/usr/bin/env bash
# backfill.sh — run extractor against all existing session JSONL files
# and append rows to run-log.csv for sessions not already logged.
set -euo pipefail

KIT_DIR="$HOME/agent-retro-kit"
RUN_LOG="$KIT_DIR/data/run-log.csv"
EXTRACTOR="$KIT_DIR/scripts/extract-run-metadata.py"
PROJECTS_DIR="$HOME/.claude/projects"

logged=0
skipped=0

for session_file in "$PROJECTS_DIR"/*/*.jsonl; do
  [ -f "$session_file" ] || continue

  session_id=$(basename "$session_file" .jsonl)

  # Skip if already logged
  if grep -q "$session_id" "$RUN_LOG" 2>/dev/null; then
    echo "[skip] $session_id already in log"
    ((skipped++)) || true
    continue
  fi

  # Skip trivially short sessions
  line_count=$(wc -l < "$session_file")
  if [ "$line_count" -lt 5 ]; then
    echo "[skip] $session_id too short ($line_count lines)"
    ((skipped++)) || true
    continue
  fi

  echo "[extract] $session_id ($line_count lines)..."

  metadata=$(python3 "$EXTRACTOR" "$session_file" 2>/dev/null) || {
    echo "[fail] extraction failed for $session_id"
    continue
  }

  get() { echo "$metadata" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null; }

  run_id="$(date +%Y-%m-%d)-backfill-${session_id:0:8}"
  captured_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  model=$(python3 -c "import json,pathlib; s=pathlib.Path('$HOME/.claude/settings.json').read_text(); d=json.loads(s); print(d.get('model','claude-sonnet-4-6'))" 2>/dev/null || echo "claude-sonnet-4-6")

  csv_field() { local v="$1"; v="${v//\"/\"\"}"; echo "\"$v\""; }

  row=$(printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$(csv_field "$run_id")" \
    "$(csv_field "$captured_at")" \
    "$(csv_field "$(get project)")" \
    "$(csv_field "$(get workspace_path)")" \
    "$(csv_field "claude_code")" \
    "$(csv_field "$model")" \
    "$(csv_field "$(get session_ref)")" \
    "$(csv_field "")" \
    "$(csv_field "$(get task_title)")" \
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
    "$(csv_field "$(get needs_review)")" \
    "$(csv_field "manual_backfill")" \
    "$(csv_field "")" \
    "$(csv_field "uncertain")" \
    "$(csv_field "")" \
    "$(csv_field "")" \
    "$(csv_field "")" \
    "$(csv_field "")" \
    "$(csv_field "uncertain")" \
    "$(csv_field "")" \
    "$(csv_field "")")

  echo "$row" >> "$RUN_LOG"
  echo "[logged] $(get task_title)"
  ((logged++)) || true
done

echo ""
echo "Backfill complete: $logged logged, $skipped skipped"
