# Agent Weekly Scorecard Template

## Week of

- Date range:
- Prepared by:
- Runs included:
- Notes on data quality:
- Baseline or comparison week:

## Headline metrics

| Metric | Current week | Previous week | Trend | Comment |
| --- | --- | --- | --- | --- |
| Total runs |  |  |  |  |
| Success rate |  |  |  | Inferred unless reviewed |
| Partial rate |  |  |  | Inferred unless reviewed |
| Failure rate |  |  |  | Inferred unless reviewed |
| Needs-review rate |  |  |  |  |
| Acceptance without edit rate |  |  |  | Reviewed subset only unless explicitly inferred |
| Median retry count |  |  |  |  |
| Loop-detected rate |  |  |  |  |
| Median total duration |  |  |  |  |
| Wrong-tool-chosen rate |  |  |  | Reviewed subset only |
| Verification-missing rate |  |  |  | Reviewed subset only |

## Interpretation guardrails

- If this is the first tracked week, mark previous week as `n/a` and use comments to capture baseline observations.
- Do not treat movement of fewer than 3 runs as a real trend unless the effect is very large.
- Prefer medians over averages for retries, duration, and token usage.
- If reviewed-run coverage is partial, label reviewer-coded rates as "reviewed subset only".
- Call out explicitly when the scorecard is mostly inference-driven.
- Segment by repo, team, model, or task type before drawing cross-cutting conclusions.

## By team or repo

| Team or repo | Runs | Success rate | Needs review | Median retries | Key note |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

## By task type

| Task type | Runs | Success rate | Needs review | Median retries | Key note |
| --- | --- | --- | --- | --- | --- |
| Feature |  |  |  |  |  |
| Bugfix |  |  |  |  |  |
| Refactor |  |  |  |  |  |
| Review |  |  |  |  |  |
| Explain |  |  |  |  |  |
| Test |  |  |  |  |  |
| Ops |  |  |  |  |  |
| Other |  |  |  |  |  |

## Top positive signals

- Example:
- Example:
- Example:

## Top failure patterns

| Pattern | Count | Example run_ids | Likely category | Comment |
| --- | --- | --- | --- | --- |
| Ambiguous task framing |  |  | Task framing / prompt |  |
| Wrong tool choice |  |  | Tool / reasoning |  |
| Missing repo or business context |  |  | Context |  |
| Unnecessary steps or over-engineering |  |  | Reasoning / workflow |  |
| Verification missing |  |  | Workflow / environment |  |

## Runs to inspect in retro

- Best run to learn from:
- Most damaging failure:
- Clean success with low retries:
- Partial or uncertain run needing review:
- Costly success worth studying:

## Recommended focus for retro

- Primary question:
- Candidate experiment:
- Metric to watch next:
- Team, repo, or workflow slice to inspect next:
