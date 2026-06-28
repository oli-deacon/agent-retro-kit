# Manual Run Log Template

Use this when you do not yet have automation, or when your collector misses a run.

## Fast rule

- Keep the inferred fields factual and short.
- Leave review fields blank unless you are intentionally doing a review pass.
- If a run needed significant human cleanup, do not count it as a clean success.
- If the outcome was not actually verified, record that explicitly.

## CSV row template

Copy this line, replace the placeholders, and append it to [run-log.csv](run-log.csv).

```csv
YYYY-MM-DD-###,YYYY-MM-DDTHH:MM:SS+0000,team-or-repo,/path/to/workspace,agent-platform,model,session-ref,ticket-ref,task-title,run-started-at,run-last-updated-at,duration-minutes,user-prompt-summary,task-type,success|partial|failure|abandoned|uncertain,yes|no|uncertain,retry-count,short-factual-summary,tool1|tool2,coding-heavy|mixed|workflow|planning-only,yes|no,sampled_clean_win|failure_or_partial_signal,,,,,,,,,
```

## Minimum fields to fill

- `run_id`
- `captured_at`
- `team_or_repo`
- `agent_platform`
- `task_title`
- `user_prompt_summary`
- `task_type_inferred`
- `outcome_inferred`
- `accepted_without_edit_inferred`
- `retry_count_inferred`
- `error_summary_inferred`
- `tool_summary`
- `coding_intensity`
- `needs_review`
- `sampling_reason`

## Review-only fields

- `outcome_reviewed`
- `accepted_without_edit_reviewed`
- `root_cause_category`
- `flags`
- `human_fix_summary`
- `reviewer_note`
- `verification_status_reviewed`
- `verification_method_reviewed`
- `verification_note_reviewed`
