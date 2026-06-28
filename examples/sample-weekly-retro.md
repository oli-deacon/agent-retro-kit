# Sample Weekly Retro

## Session details

- Date: 2026-06-28
- Facilitator: Example operator
- Participants: Team lead, engineer, agent operator
- Run range reviewed: 2026-06-22-001 to 2026-06-28-018
- Scorecard reference: `examples/sample-weekly-scorecard.md`
- Previous experiment review: Explicit verification plans helped, but feature work still expanded too easily after the first success.

## 1. Sprint summary

- Total runs analysed: 18
- Success rate: 61%
- Partial rate: 28%
- Failure rate: 11%
- Needs-review rate: 50%
- Acceptance without edit rate: 22%
- Average or median retry count: Median 4
- Most common task type: Feature
- Teams or repos represented: payments-platform, docs-site, internal-tools
- Most common failure mode: Scope drift and missing verification on feature work

## 2. What worked well

- What the agent or operator did: Started with smaller bugfix slices and clearer finish lines
- Which run_ids demonstrate it: 2026-06-25-002, 2026-06-26-003
- Why it contributed to success: The work stayed focused and needed fewer retries

- What the agent or operator did: Called out blocked verification instead of overstating completion
- Which run_ids demonstrate it: 2026-06-24-002, 2026-06-27-001
- Why it contributed to success: The team avoided false confidence

## 3. What caused failures or costly success

- What went wrong: Feature threads expanded into follow-on cleanup after the original task was effectively done
- Which run_ids demonstrate it: 2026-06-24-005, 2026-06-26-002
- Which teams or repos they came from: payments-platform
- Whether the issue is inferred or confirmed in review: Confirmed in review
- The first step or moment where it appeared: Immediately after the first deploy or initial success
- Whether it was mainly prompt, task framing, context, tool, workflow, reasoning, or environment related: Workflow / task framing

- What went wrong: Missing environment knowledge blocked confident verification
- Which run_ids demonstrate it: 2026-06-24-002, 2026-06-27-001
- Which teams or repos they came from: payments-platform, internal-tools
- Whether the issue is inferred or confirmed in review: Confirmed in review
- The first step or moment where it appeared: Verification stage
- Whether it was mainly prompt, task framing, context, tool, workflow, reasoning, or environment related: Environment / context

## 4. Root cause deep dive

- Why did feature runs stay expensive even when they shipped?
  Because the first slice was still too broad.
- Why was the first slice too broad?
  Because the task brief did not force a smallest viable first slice.
- Why did that matter?
  Because follow-on cleanup stayed inside the same run instead of becoming a separate decision.
- Why was cleanup not split out?
  Because the finish line was defined loosely.
- Why was the finish line loose?
  Because the operator prioritized momentum over scope control.

Root cause statement:

- Root cause in one sentence: Feature runs became costly because the workflow did not force a smallest viable first slice and clear stop point before implementation began.
- Primary category: Task framing / workflow

## 5. Start / Stop / Continue

### Start

- Add a smallest-viable-slice check to the complex task brief
- Require explicit verification planning for production-facing work
- Split post-success cleanup into a new run unless it is critical to the first outcome

### Stop

- Stop treating a broad feature request as one uninterrupted run by default
- Stop calling work done when only local verification passed
- Stop changing prompts before checking for workflow causes

### Continue

- Continue reviewing one clean win every week
- Continue using partial outcomes honestly
- Continue tracking costly success separately from obvious failure

## 6. Experiment decisions

| Experiment | Hypothesis | Owner | Start date | Metric to watch | Review date |
| --- | --- | --- | --- | --- | --- |
| EXP-004 Smaller first slices | Narrower first slices will reduce retries on feature work | Example operator | 2026-06-29 | Median retries on feature work | 2026-07-06 |
| EXP-005 Explicit verification gate | Naming verification before implementation will reduce blocked outcomes | Team lead | 2026-06-29 | Verification-missing rate | 2026-07-06 |

## 7. Actions agreed

| Action | Type | Owner | Due date | Status |
| --- | --- | --- | --- | --- |
| Update the complex task brief | Workflow | Example operator | 2026-06-29 | Open |
| Review 3 blocked runs for environment causes | Measurement | Team lead | 2026-07-02 | Open |
| Add a short operator checklist for production work | Workflow | Engineer | 2026-07-02 | Open |

## 8. Watch items

- Internal-tools sample size is still small
- Manual timing may undercount passive wait time
- One run may have combined two real tasks

## 9. Cadence check

- Did we review the scorecard this week? Yes
- Did we inspect at least 2 supporting runs for each repeated pattern? Yes
- Did we leave with only 1-2 experiments? Yes
- Is any logging field too costly to maintain? No

## 10. Decision log entry

- Decision: Add a smallest-viable-slice rule and explicit verification planning for feature work
- Why: Costly success is now more common than outright failure
- Evidence: 2026-06-24-002, 2026-06-24-005, 2026-06-26-002, 2026-06-27-001
- Revisit date: 2026-07-06
