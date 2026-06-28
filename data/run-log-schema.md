# Agent Run Log Schema

This schema is designed for tool-agnostic agent retros.

It works whether your evidence comes from manual notes, exported transcripts, a custom collector, or a mix of all three.

## Collection model

- An agent run is one meaningful request or execution thread.
- The source of truth can be a chat thread, terminal session, ticket-linked interaction, or manual operator note.
- Manual logging is enough to begin.
- Automated capture should fill inference fields and leave review fields blank until weekly review.

## Log layers

The central CSV keeps auto-captured and human-reviewed fields together, but they serve different jobs.

### Auto-captured or operator-entered fields

| Field | Description | Example |
| --- | --- | --- |
| `run_id` | Stable identifier for one captured run | `2026-06-28-001` |
| `captured_at` | When the row was logged | `2026-06-28T18:10:00+1000` |
| `team_or_repo` | Team, product area, or repo label | `payments-platform` |
| `workspace_path` | Optional workspace or repo path | `/workspace/payments-platform` |
| `agent_platform` | Agent system used for the run | `claude_code` |
| `model` | Optional model label | `claude-sonnet-4` |
| `session_ref` | Optional thread or session identifier | `abc123` |
| `ticket_ref` | Optional Jira, Linear, or issue reference | `PAY-1842` |
| `task_title` | Short title of the run | `Add retry handling to webhook sync` |
| `run_started_at` | Start timestamp when known | `2026-06-28T10:56:42+1000` |
| `run_last_updated_at` | Latest activity timestamp when known | `2026-06-28T11:42:05+1000` |
| `duration_minutes_inferred` | Duration estimate when available | `46` |
| `user_prompt_summary` | Short summary of the starting ask | `Fix webhook sync retries and verify staging behavior` |
| `task_type_inferred` | Inferred task type | `bugfix` |
| `outcome_inferred` | `success`, `partial`, `failure`, `abandoned`, or `uncertain` | `partial` |
| `accepted_without_edit_inferred` | `yes`, `no`, or `uncertain` | `no` |
| `retry_count_inferred` | Conservative retry estimate | `3` |
| `error_summary_inferred` | Short factual outcome or problem summary | `Staging flow passed, but production auth scope remained unresolved` |
| `tool_summary` | Pipe-separated summary of meaningful tools or systems touched | `edit|tests|terminal|deploy|browser` |
| `coding_intensity` | `coding-heavy`, `mixed`, `workflow`, or `planning-only` | `coding-heavy` |
| `needs_review` | `yes` when a human should inspect later | `yes` |
| `sampling_reason` | Why the row was captured | `failure_or_partial_signal` |

### Human-reviewed fields

These stay blank at capture time and are filled during weekly review or focused follow-up.

| Field | Description | Example |
| --- | --- | --- |
| `outcome_reviewed` | Human-confirmed outcome when inference needs correction | `partial` |
| `accepted_without_edit_reviewed` | Human-confirmed edit status | `no` |
| `root_cause_category` | `prompt`, `task_framing`, `context`, `tool`, `workflow`, `reasoning`, `environment`, or `mixed` | `workflow` |
| `flags` | Pipe-separated review flags | `verification_missing|wrong_tool_chosen` |
| `human_fix_summary` | Short summary of what the human had to do | `Split deploy verification into a smaller follow-up and checked staging auth manually` |
| `reviewer_note` | 1-3 sentences of review context | `Implementation worked locally, but live verification was blocked by missing production scope.` |
| `verification_status_reviewed` | Human-confirmed verification state for the user outcome | `blocked` |
| `verification_method_reviewed` | How verification was attempted or completed | `local_run|staging_check` |
| `verification_note_reviewed` | Short note on what was verified or what blocked it | `Staging confirmed; production verification blocked by permission boundary.` |

## Controlled vocabularies

### `task_type_inferred`

- `feature`
- `bugfix`
- `refactor`
- `review`
- `explain`
- `test`
- `ops`
- `other`

### `outcome_inferred` and `outcome_reviewed`

- `success`
- `partial`
- `failure`
- `abandoned`
- `uncertain`

### `accepted_without_edit_inferred` and `accepted_without_edit_reviewed`

- `yes`
- `no`
- `uncertain`

### `coding_intensity`

- `coding-heavy`
- `mixed`
- `workflow`
- `planning-only`

### `verification_status_reviewed`

- `completed`
- `blocked`
- `not_needed`
- `uncertain`

### `sampling_reason`

- `failure_or_partial_signal`
- `heavy_retry_signal`
- `blocker_or_escalation_signal`
- `sampled_clean_win`
- `manual_backfill`

### `flags`

- `prompt_was_ambiguous`
- `acceptance_criteria_unclear`
- `user_request_needed_clarification`
- `insufficient_repo_context`
- `wrong_tool_chosen`
- `unnecessary_steps`
- `missed_existing_code`
- `over_engineered`
- `hallucinated_api_or_function`
- `correct_but_slow`
- `verification_missing`
- `loop_detected`

## Verification review rules

- Use `verification_status_reviewed=completed` when the user-visible or system-visible outcome was actually confirmed.
- Use `verification_status_reviewed=blocked` when the code may be shipped but the outcome could not be confirmed because of environment, access, deploy, or platform constraints.
- Use `verification_status_reviewed=not_needed` for runs where user-outcome verification is not a meaningful concept.
- Keep `verification_method_reviewed` short and factual, such as `local_run`, `staging_check`, `prod_check`, `browser_check`, `artifact_review`, or `not_applicable`.
- Use `verification_note_reviewed` to capture the blocking constraint or the exact thing that was confirmed.
- If `verification_status_reviewed=blocked`, also prefer the `verification_missing` flag unless a more specific reviewed convention replaces it later.

## Inference rules

- Prefer conservative inference over false precision.
- If the evidence signals unresolved runtime, deploy, or verification state, infer `partial` or `failure` rather than `success`.
- Use `uncertain` when the evidence is mixed.
- Keep `retry_count_inferred` bounded and approximate. Count meaningful restart or correction behavior, not every tool call.
- Skip planning-only threads unless you intentionally sample them as clean wins.

## Review rules

- `needs_review=yes` for likely `partial`, `failure`, `uncertain`, or heavily iterative runs.
- Clean sampled wins can remain unreviewed unless selected in retro.
- Review fills human fields; it should not overwrite inferred fields unless the inference is clearly wrong.
- When a reviewed row depends on runtime, deploy, or user-visible behavior, fill the verification review fields instead of relying on `reviewer_note` alone.
