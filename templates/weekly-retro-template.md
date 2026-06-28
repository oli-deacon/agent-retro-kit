# Agent Weekly Retrospective Template

## Session details

- Date:
- Facilitator:
- Participants:
- Run range reviewed:
- Scorecard reference:
- Previous experiment review:

## 1. Sprint summary

- Total runs analysed:
- Success rate:
- Partial rate:
- Failure rate:
- Needs-review rate:
- Acceptance without edit rate:
- Average or median retry count:
- Most common task type:
- Teams or repos represented:
- Most common failure mode:

## 2. What worked well

List up to 5 specific behaviors, usage patterns, or workflow choices that helped successful runs.

For each item capture:

- What the agent or operator did
- Which run_ids demonstrate it
- Why it contributed to success

## 3. What caused failures or costly success

List up to 5 repeated patterns from failed, partial, or high-effort runs.

For each item capture:

- What went wrong
- Which run_ids demonstrate it
- Which teams or repos they came from
- Whether the issue is inferred or confirmed in review
- The first step or moment where it appeared
- Whether it was mainly prompt, task framing, context, tool, workflow, reasoning, or environment related

## 4. Root cause deep dive

Choose the single most damaging repeated pattern and run 5 Whys.

- Why did this happen?
- Why did that happen?
- Why did that happen?
- Why did that happen?
- Why did that happen?

Root cause statement:

- Root cause in one sentence:
- Primary category:

## 5. Start / Stop / Continue

### Start

Add these instructions, checks, or workflow rules:

- 
- 
- 

### Stop

Remove, replace, or constrain these patterns:

- 
- 
- 

### Continue

Preserve these behaviors or instructions:

- 
- 
- 

## 6. Experiment decisions

Select no more than 1-2 experiments.

| Experiment | Hypothesis | Owner | Start date | Metric to watch | Review date |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

## 7. Actions agreed

| Action | Type | Owner | Due date | Status |
| --- | --- | --- | --- | --- |
|  | Prompt |  |  |  |
|  | Tooling |  |  |  |
|  | Workflow |  |  |  |
|  | Measurement |  |  |  |

## 8. Watch items

Capture patterns seen in only one run or where evidence is still weak.

- 
- 
- 

## 9. Cadence check

- Did we review the scorecard this week?
- Did we inspect at least 2 supporting runs for each repeated pattern?
- Did we leave with only 1-2 experiments?
- Is any logging field too costly to maintain?

## 10. Decision log entry

- Decision:
- Why:
- Evidence:
- Revisit date:

## Facilitation guardrails

- Do not recommend changes based on only one run
- Treat inference as provisional until a human review confirms or corrects it
- Treat accepted_without_edit false with outcome success as partial value, not clean success
- Do not optimize for lower token cost alone
- Separate prompt issues from context, tooling, workflow, reasoning, and environment issues
- Prefer small reversible changes
