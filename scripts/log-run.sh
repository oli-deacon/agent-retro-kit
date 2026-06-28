#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$ROOT_DIR/data/run-log.csv"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "Run log not found: $LOG_FILE" >&2
  exit 1
fi

now_iso="$(date '+%Y-%m-%dT%H:%M:%S%z')"
today="$(date +%F)"

csv_escape() {
  local value="${1:-}"
  value=${value//$'\n'/ }
  value=${value//\"/\"\"}
  printf '"%s"' "$value"
}

next_run_id() {
  local date_prefix="$1"
  local next_seq
  next_seq="$(
    awk -F',' -v prefix="$date_prefix" '
      NR == 1 { next }
      {
        first = $1
        gsub(/^"/, "", first)
        gsub(/"$/, "", first)
        if (index(first, prefix "-") == 1) {
          n = substr(first, length(prefix) + 2) + 0
          if (n > max) max = n
        }
      }
      END { printf "%03d", max + 1 }
    ' "$LOG_FILE"
  )"
  printf "%s-%s" "$date_prefix" "$next_seq"
}

prompt() {
  local label="$1"
  local default_value="${2-}"
  local value

  if [[ -n "$default_value" ]]; then
    read -r -p "$label [$default_value]: " value
    printf '%s' "${value:-$default_value}"
  else
    read -r -p "$label: " value
    printf '%s' "$value"
  fi
}

run_id="$(next_run_id "$today")"
team_or_repo="${1:-}"
agent_platform="${2:-}"
task_type_inferred="${3:-}"
outcome_inferred="${4:-}"

echo "Logging a run to $LOG_FILE"
echo "Generated run_id: $run_id"

captured_at="$now_iso"
team_or_repo="$(prompt "Team or repo" "${team_or_repo:-}")"
workspace_path="$(prompt "Workspace path (optional)" "")"
agent_platform="$(prompt "Agent platform" "${agent_platform:-claude_code}")"
model="$(prompt "Model (optional)" "")"
session_ref="$(prompt "Session or thread ref (optional)" "")"
ticket_ref="$(prompt "Ticket ref (optional)" "")"
task_title="$(prompt "Task title" "")"
run_started_at="$(prompt "Run started at (optional ISO timestamp)" "$now_iso")"
run_last_updated_at="$(prompt "Run last updated at (optional ISO timestamp)" "$now_iso")"
duration_minutes_inferred="$(prompt "Duration minutes inferred (optional)" "")"
user_prompt_summary="$(prompt "User prompt summary" "")"
task_type_inferred="$(prompt "Task type inferred" "${task_type_inferred:-feature}")"
outcome_inferred="$(prompt "Outcome inferred" "${outcome_inferred:-success}")"
accepted_without_edit_inferred="$(prompt "Accepted without edit inferred" "uncertain")"
retry_count_inferred="$(prompt "Retry count inferred" "0")"
error_summary_inferred="$(prompt "Short factual error or outcome summary" "")"
tool_summary="$(prompt "Tool summary (pipe-separated)" "")"
coding_intensity="$(prompt "Coding intensity" "coding-heavy")"
needs_review="$(prompt "Needs review" "no")"
sampling_reason_default="manual_backfill"
if [[ "$needs_review" == "yes" ]]; then
  sampling_reason_default="failure_or_partial_signal"
fi
sampling_reason="$(prompt "Sampling reason" "$sampling_reason_default")"

outcome_reviewed=""
accepted_without_edit_reviewed=""
root_cause_category=""
flags=""
human_fix_summary=""
reviewer_note=""
verification_status_reviewed=""
verification_method_reviewed=""
verification_note_reviewed=""

add_review="no"
if [[ "$needs_review" == "yes" ]]; then
  add_review="$(prompt "Add review detail now? (yes/no)" "no")"
fi

if [[ "$add_review" == "yes" ]]; then
  outcome_reviewed="$(prompt "Outcome reviewed (optional)" "")"
  accepted_without_edit_reviewed="$(prompt "Accepted without edit reviewed (optional)" "")"
  root_cause_category="$(prompt "Root cause category (optional)" "")"
  flags="$(prompt "Flags, pipe-separated (optional)" "")"
  human_fix_summary="$(prompt "Human fix summary (optional)" "")"
  reviewer_note="$(prompt "Reviewer note (optional)" "")"
  verification_status_reviewed="$(prompt "Verification status reviewed (completed/blocked/not_needed/uncertain, optional)" "")"
  verification_method_reviewed="$(prompt "Verification method reviewed (optional)" "")"
  verification_note_reviewed="$(prompt "Verification note reviewed (optional)" "")"
fi

row="$(
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$(csv_escape "$run_id")" \
    "$(csv_escape "$captured_at")" \
    "$(csv_escape "$team_or_repo")" \
    "$(csv_escape "$workspace_path")" \
    "$(csv_escape "$agent_platform")" \
    "$(csv_escape "$model")" \
    "$(csv_escape "$session_ref")" \
    "$(csv_escape "$ticket_ref")" \
    "$(csv_escape "$task_title")" \
    "$(csv_escape "$run_started_at")" \
    "$(csv_escape "$run_last_updated_at")" \
    "$(csv_escape "$duration_minutes_inferred")" \
    "$(csv_escape "$user_prompt_summary")" \
    "$(csv_escape "$task_type_inferred")" \
    "$(csv_escape "$outcome_inferred")" \
    "$(csv_escape "$accepted_without_edit_inferred")" \
    "$(csv_escape "$retry_count_inferred")" \
    "$(csv_escape "$error_summary_inferred")" \
    "$(csv_escape "$tool_summary")" \
    "$(csv_escape "$coding_intensity")" \
    "$(csv_escape "$needs_review")" \
    "$(csv_escape "$sampling_reason")" \
    "$(csv_escape "$outcome_reviewed")" \
    "$(csv_escape "$accepted_without_edit_reviewed")" \
    "$(csv_escape "$root_cause_category")" \
    "$(csv_escape "$flags")" \
    "$(csv_escape "$human_fix_summary")" \
    "$(csv_escape "$reviewer_note")" \
    "$(csv_escape "$verification_status_reviewed")" \
    "$(csv_escape "$verification_method_reviewed")" \
    "$(csv_escape "$verification_note_reviewed")"
)"

printf '%s\n' "$row" >> "$LOG_FILE"

echo
echo "Appended run $run_id"
