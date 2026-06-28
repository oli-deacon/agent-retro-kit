# Sample Weekly Scorecard

## Week of

- Date range: 2026-06-22 to 2026-06-28
- Prepared by: Example operator
- Runs included: 18
- Notes on data quality: Mostly manual logging; reviewed subset of 6 runs
- Baseline or comparison week: 2026-06-15 to 2026-06-21

## Headline metrics

| Metric | Current week | Previous week | Trend | Comment |
| --- | --- | --- | --- | --- |
| Total runs | 18 | 14 | Up | Slightly higher volume |
| Success rate | 61% | 57% | Up | Mostly inferred |
| Partial rate | 28% | 29% | Flat |  |
| Failure rate | 11% | 14% | Down | Small sample |
| Needs-review rate | 50% | 64% | Down | Better distribution |
| Acceptance without edit rate | 22% | 14% | Up | Reviewed subset only |
| Median retry count | 4 | 6 | Down | Clear improvement |
| Loop-detected rate | 11% | 21% | Down | Reviewed subset only |
| Median total duration | 42 min | 67 min | Down | Manual timing |
| Wrong-tool-chosen rate | 17% | 33% | Down | Reviewed subset only |
| Verification-missing rate | 33% | 50% | Down | Reviewed subset only |

## By team or repo

| Team or repo | Runs | Success rate | Needs review | Median retries | Key note |
| --- | --- | --- | --- | --- | --- |
| payments-platform | 10 | 60% | 50% | 4 | Verification still costly |
| docs-site | 5 | 80% | 20% | 1 | Clean wins dominated |
| internal-tools | 3 | 33% | 100% | 7 | Context gaps |

## By task type

| Task type | Runs | Success rate | Needs review | Median retries | Key note |
| --- | --- | --- | --- | --- | --- |
| Feature | 8 | 50% | 75% | 5 | Costly successes dominate |
| Bugfix | 4 | 75% | 25% | 2 | Better outcomes |
| Refactor | 2 | 50% | 50% | 3 | Limited sample |
| Review | 2 | 100% | 0% | 1 | Clean and fast |
| Explain | 1 | 100% | 0% | 0 |  |
| Ops | 1 | 0% | 100% | 8 | Environment blocked |

## Top positive signals

- Smaller task slices reduced retries in bugfix work
- Explicit verification plans improved honesty of outcomes
- Reviewing one clean win helped identify a reusable workflow

## Top failure patterns

| Pattern | Count | Example run_ids | Likely category | Comment |
| --- | --- | --- | --- | --- |
| Verification missing | 3 | 2026-06-24-002, 2026-06-25-004 | Workflow / environment | Mostly production checks |
| Missing repo or business context | 3 | 2026-06-23-003, 2026-06-27-001 | Context | Internal tools worst hit |
| Scope drift after initial success | 2 | 2026-06-24-005, 2026-06-26-002 | Workflow / task framing | Costly success pattern |

## Runs to inspect in retro

- Best run to learn from: 2026-06-26-003
- Most damaging failure: 2026-06-27-001
- Clean success with low retries: 2026-06-25-002
- Partial or uncertain run needing review: 2026-06-24-002
- Costly success worth studying: 2026-06-26-002

## Recommended focus for retro

- Primary question: Why are feature tasks still expensive even when they ship?
- Candidate experiment: Add a smallest-viable-slice check before implementation starts
- Metric to watch next: Median retries on feature work
- Team, repo, or workflow slice to inspect next: payments-platform feature tasks
