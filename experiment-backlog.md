# Agent Experiment Backlog

## How to use this backlog

Each experiment should be small, testable, and tied to a metric. Avoid permanent changes by default. Test first, then keep, modify, or revert.

`experiments.json` is the machine-readable source used by the dashboard. Keep this Markdown file for the decision narrative. When a collector actually applies an experiment, record the assignment with:

```bash
python3 scripts/record-experiment-exposure.py EXP-001 RUN-ID --variant treatment
```

Only explicit rows in `data/experiment-exposures.csv` count toward results. This prevents eligible-but-untreated runs from contaminating the evaluation.

## Experiment list

| ID | Experiment | Hypothesis | Type | Owner | Date added | Status | Target metric | Review date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EXP-001 |  |  | Prompt / Tool / Workflow / Context / Task template / Measurement |  |  | Proposed |  |  |
| EXP-002 |  |  | Prompt / Tool / Workflow / Context / Task template / Measurement |  |  | Proposed |  |  |
| EXP-003 |  |  | Prompt / Tool / Workflow / Context / Task template / Measurement |  |  | Proposed |  |  |

## Experiment detail template

### Experiment ID

- Title:
- Status:
- Owner:
- Date added:
- Start date:
- Review date:

### Problem to solve

- What repeated pattern are we addressing?
- Which run_ids support the pattern?

### Change

- What exactly will we change?
- Where will the change be made?

### Hypothesis

- We believe that:
- Because:

### Success criteria

- Primary metric:
- Current value:
- Target value:
- Secondary signals:

### Guardrails

- What risks could this introduce?
- What would cause us to stop or revert quickly?

### Review outcome

- Outcome:
- What happened in the data?
- Keep / modify / revert:
- Notes:
