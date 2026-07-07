# Claude Code Integration

Automated run logging for [Claude Code](https://claude.ai/code) (Anthropic's CLI agent).

## How it works

Claude Code stores every session as a JSONL file at `~/.claude/projects/<project>/`. This integration reads those files to extract retro metadata automatically, then wires a global `Stop` hook so logging fires after every session.

```
Session ends
  → Stop hook fires
  → auto-log.sh runs
  → reads session JSONL from ~/.claude/projects/
  → extract-run-metadata.py infers structured fields
  → appends pre-filled row to run-log.csv
  → prompts for 2 human-review fields (30 seconds)
```

## Auto-captured fields

| Field | Source |
|---|---|
| `session_ref` | JSONL filename |
| `project` | Project directory slug |
| `run_started_at` / `run_last_updated_at` | First/last timestamps in JSONL |
| `duration_minutes_inferred` | Computed from timestamps |
| `task_title` | First user message |
| `task_type_inferred` | Keyword matching on first prompt |
| `outcome_inferred` | Heuristic: success signals vs. error patterns |
| `retry_count_inferred` | Count of tool error recovery loops |
| `tool_summary` | Pipe-separated tool names used |
| `coding_intensity` | Derived from edit/bash/read tool ratios |
| `needs_review` | Set when outcome is uncertain/partial/failure |
| `flags` | loop_detected, verification_missing (rule-based) |
| `model` | Read from `~/.claude/settings.json` |

## Fields requiring human input (prompted after each session)

- `accepted_without_edit_reviewed` — did you use the output as-is?
- `verification_status_reviewed` — did you verify the outcome?

## Setup

**1. Install globally**
```sh
git clone https://github.com/oli-deacon/agent-retro-kit ~/agent-retro-kit
```

**2. Wire the Stop hook** — add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash $HOME/agent-retro-kit/integrations/claude-code/auto-log.sh"
          }
        ]
      }
    ]
  }
}
```

**3. Backfill existing sessions**
```sh
bash ~/agent-retro-kit/integrations/claude-code/backfill.sh
```

## Requirements

- macOS or Linux with bash
- Python 3.9+
- Claude Code with sessions stored at `~/.claude/projects/`
- No API key required — extraction is fully rule-based

## Notes

- Sessions shorter than 5 lines are skipped automatically
- Sessions already in the log are skipped (dedup by `session_ref`)
- Duration inflation from multi-day sessions is filtered out in `generate-weekly-docs.py`
- The `accepted_without_edit` field can be improved by diffing git state before/after the session (future enhancement)
