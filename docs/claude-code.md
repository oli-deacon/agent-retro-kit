# Using This Kit With Claude Code

This guide keeps the kit generic while giving you a practical workflow for Claude Code.

## Recommended operating pattern

Treat one meaningful Claude Code task or thread as one run.

Log a run when:

- a real implementation task finishes
- a task ends in a blocked or partial state
- a task technically succeeds but required too much rework
- a thread drifted enough that it became a new task

## Minimum fields I would capture

For a lightweight workplace rollout, fill these first:

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
- `needs_review`

Set:

- `agent_platform=claude_code`
- `model` if it is easy to capture and useful internally

## What counts as a retry

Count meaningful rework, not every message.

Examples that usually count:

- redoing a broken implementation approach
- switching tools or workflows after the first path failed
- follow-up repair loops after the first "done"
- repeated deploy or verification correction cycles

Examples that usually do not count:

- small clarifying turns
- ordinary edits inside one working implementation path
- a single test-fix-test cycle that stays straightforward

## How I would classify outcomes

- `success`: the intended outcome was delivered and did not need meaningful human rescue
- `partial`: useful progress happened, but the outcome stayed blocked, unverified, or required significant human cleanup
- `failure`: the run did not produce usable progress or ended in the wrong place
- `abandoned`: the run stopped before a meaningful outcome was pursued to completion
- `uncertain`: the available evidence is too weak to classify honestly

## Verification rule

Do not let "code changed" stand in for "outcome verified."

For Claude Code work, explicitly separate:

- implementation complete
- tests complete
- local verification complete
- staging or production verification complete

If the final user-visible result was not confirmed, prefer `partial` or mark verification as blocked in review.

## Suggested weekly review sample

Each week, review:

- 1 clean success
- 1 costly success
- 1 blocked or partial run
- 1 run with obvious human cleanup
- 1 run that points to poor task framing or missing context

## Prompting changes to test carefully

Claude Code users often overreact by rewriting prompts too often.

Before changing prompts, ask whether the real issue was:

- the task was too broad
- the finish line was unclear
- the repo context was missing
- verification was impossible in the environment
- the operator kept expanding scope mid-thread

If yes, prefer workflow changes first.

## A simple workplace rollout

Week 1:

- log 10-20 meaningful runs
- run `scripts/bootstrap-weekly-cycle.sh`
- do not try to automate yet
- establish a baseline scorecard

Week 2:

- run the first retro
- pick one workflow experiment and optionally one prompt experiment

Week 3 onward:

- keep the logging small
- review the most expensive runs, not the most dramatic ones
- revert experiments that do not help
