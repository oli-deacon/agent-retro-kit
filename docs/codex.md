# Using This Kit With Codex

This guide keeps the kit generic while giving you a practical workflow for Codex.

## Recommended operating pattern

Treat one meaningful Codex thread or one clearly bounded user request as one run.

Log a run when:

- a real implementation or debugging task finishes
- a task ends in a blocked or partial state
- a task technically succeeds but required too much iteration or cleanup
- a thread drifted into a materially different task and should really count as a separate run

## Minimum fields I would capture

For a lightweight rollout, fill these first:

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

- `agent_platform=codex`
- `model` if it is easy to capture and useful later

## What counts as a retry

Count meaningful rework, not every tool call or assistant update.

Examples that usually count:

- switching implementation approach after the first path failed
- repeated fix-test-fix cycles because the first solution was wrong
- deploy or verification loops after the task looked "done"
- reopening the same task inside the thread because the real finish line was not met

Examples that usually do not count:

- ordinary tool use inside one working approach
- short clarification exchanges
- one straightforward test-fix-test pass

## How I would classify outcomes

- `success`: the intended outcome was delivered and did not need meaningful human rescue
- `partial`: useful progress happened, but the final outcome stayed blocked, unverified, or needed significant human cleanup
- `failure`: the run did not produce a usable result
- `abandoned`: the run stopped before completion was seriously pursued
- `uncertain`: the evidence is too weak to classify honestly

## Verification rule

Do not treat "files changed" as the same thing as "outcome verified."

For Codex work, explicitly separate:

- code changed
- local checks passed
- user-visible behavior verified
- deploy or runtime behavior verified

If the final outcome was not actually confirmed, prefer `partial` or mark verification as blocked in review.

## Common Codex patterns worth reviewing

These often produce the best retro insights:

- expensive success after many iterations
- verification blocked by environment or access limits
- task framing that was too broad for one thread
- tool choice that created avoidable work
- honest partial outcomes that prevented false success

## Prompting and workflow changes to test carefully

Before changing prompts, ask whether the real issue was:

- the request needed a smaller first slice
- the finish line was unclear
- the repo or business context was missing
- verification was blocked by environment constraints
- the workflow encouraged keeping follow-on cleanup inside the same thread

If yes, prefer workflow changes before prompt changes.

## A simple rollout

Week 1:

- log 10-20 meaningful runs
- run `scripts/bootstrap-weekly-cycle.sh`
- establish a baseline scorecard
- do not over-automate yet

Week 2:

- run the first retro
- pick one workflow experiment and at most one prompt experiment

Week 3 onward:

- keep the logging light
- study costly success as seriously as outright failure
- revert experiments that do not help
