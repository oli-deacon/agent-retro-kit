#!/usr/bin/env python3
"""
generate-weekly-docs.py

Reads run-log.csv and generates a pre-populated weekly scorecard and retro doc
for the current (or specified) ISO week.

Usage:
  python3 generate-weekly-docs.py            # current week
  python3 generate-weekly-docs.py 2026-W26   # specific week
"""

import csv
import sys
import statistics
import pathlib
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

KIT_DIR = pathlib.Path.home() / "agent-retro-kit"
RUN_LOG = KIT_DIR / "data" / "run-log.csv"
SCORECARDS_DIR = KIT_DIR / "scorecards"
RETROS_DIR = KIT_DIR / "retros"

# ── date helpers ──────────────────────────────────────────────────────────────

def iso_week_label(dt: datetime) -> str:
    return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"


def week_date_range(year: int, week: int) -> tuple[str, str]:
    monday = datetime.fromisocalendar(year, week, 1)
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def parse_week_arg(arg: str) -> tuple[int, int]:
    try:
        dt = datetime.strptime(arg, "%Y-W%W")
        iso = dt.isocalendar()
        return iso[0], iso[1]
    except ValueError:
        pass
    try:
        year, w = arg.split("-W")
        return int(year), int(w)
    except Exception:
        raise ValueError(f"Could not parse week: {arg!r}. Use format 2026-W26")


def captured_week(row: dict) -> str:
    ts = row.get("captured_at") or row.get("run_started_at", "")
    try:
        dt = datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return iso_week_label(dt)
    except Exception:
        return ""


# ── CSV loading ───────────────────────────────────────────────────────────────

def load_runs(week_label: str, prev_week_label: str) -> tuple[list, list]:
    if not RUN_LOG.exists():
        return [], []
    with RUN_LOG.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    current = [r for r in rows if captured_week(r) == week_label]
    previous = [r for r in rows if captured_week(r) == prev_week_label]
    return current, previous


# ── metric helpers ────────────────────────────────────────────────────────────

def pct(count: int, total: int) -> str:
    if total == 0:
        return "n/a"
    return f"{round(count / total * 100)}%"


def outcome_counts(runs: list) -> dict:
    c = Counter()
    for r in runs:
        outcome = r.get("outcome_reviewed") or r.get("outcome_inferred") or "uncertain"
        c[outcome] += 1
    return c


def median_retries(runs: list) -> str:
    vals = []
    for r in runs:
        try:
            vals.append(int(r.get("retry_count_inferred", 0) or 0))
        except ValueError:
            pass
    if not vals:
        return "n/a"
    return str(int(statistics.median(vals)))


def median_duration(runs: list) -> str:
    vals = []
    for r in runs:
        try:
            v = int(r.get("duration_minutes_inferred", 0) or 0)
            if 0 < v < 1440:  # ignore inflated multi-day durations
                vals.append(v)
        except ValueError:
            pass
    if not vals:
        return "n/a"
    return f"{int(statistics.median(vals))} min"


def flag_rate(runs: list, flag: str) -> str:
    count = sum(1 for r in runs if flag in (r.get("flags") or ""))
    return pct(count, len(runs))


def acceptance_rate(runs: list) -> str:
    reviewed = [r for r in runs if r.get("accepted_without_edit_reviewed") in ("yes", "no")]
    inferred = [r for r in runs if r.get("accepted_without_edit_inferred") in ("yes", "no")]
    pool = reviewed if reviewed else inferred
    if not pool:
        return "n/a"
    yes = sum(1 for r in pool if (r.get("accepted_without_edit_reviewed") or r.get("accepted_without_edit_inferred")) == "yes")
    suffix = " (reviewed)" if reviewed else " (inferred)"
    return pct(yes, len(pool)) + suffix


def by_project(runs: list) -> list[dict]:
    groups = defaultdict(list)
    for r in runs:
        groups[r.get("team_or_repo") or "unknown"].append(r)
    result = []
    for proj, proj_runs in sorted(groups.items()):
        oc = outcome_counts(proj_runs)
        result.append({
            "project": proj,
            "runs": len(proj_runs),
            "success_rate": pct(oc.get("success", 0), len(proj_runs)),
            "needs_review": pct(sum(1 for r in proj_runs if r.get("needs_review") == "yes"), len(proj_runs)),
            "median_retries": median_retries(proj_runs),
        })
    return result


def by_task_type(runs: list) -> list[dict]:
    task_types = ["feature", "bugfix", "refactor", "review", "explain", "test", "ops", "other"]
    result = []
    for tt in task_types:
        tt_runs = [r for r in runs if r.get("task_type_inferred") == tt]
        if not tt_runs:
            result.append({"type": tt.capitalize(), "runs": 0, "success_rate": "n/a",
                           "needs_review": "n/a", "median_retries": "n/a"})
            continue
        oc = outcome_counts(tt_runs)
        result.append({
            "type": tt.capitalize(),
            "runs": len(tt_runs),
            "success_rate": pct(oc.get("success", 0), len(tt_runs)),
            "needs_review": pct(sum(1 for r in tt_runs if r.get("needs_review") == "yes"), len(tt_runs)),
            "median_retries": median_retries(tt_runs),
        })
    return result


def top_flags(runs: list) -> list[tuple[str, int, list]]:
    flag_map = defaultdict(list)
    for r in runs:
        for f in (r.get("flags") or "").split("|"):
            f = f.strip()
            if f:
                flag_map[f].append(r.get("run_id", ""))
    return sorted(flag_map.items(), key=lambda x: -len(x[1]))


def runs_to_inspect(runs: list) -> dict:
    needs = [r for r in runs if r.get("needs_review") == "yes"]
    successes = [r for r in runs if (r.get("outcome_reviewed") or r.get("outcome_inferred")) == "success"]
    failures = [r for r in runs if (r.get("outcome_reviewed") or r.get("outcome_inferred")) == "failure"]
    partials = [r for r in runs if (r.get("outcome_reviewed") or r.get("outcome_inferred")) == "partial"]

    def title(r):
        return r.get("task_title", r.get("run_id", ""))[:60]

    def fmt(r):
        return f"`{r['run_id']}` — {title(r)}" if r else "none this week"

    low_retry_success = sorted(successes, key=lambda r: int(r.get("retry_count_inferred") or 0))
    return {
        "best_win": fmt(low_retry_success[0]) if low_retry_success else "none this week",
        "worst_failure": fmt(failures[-1]) if failures else "none this week",
        "clean_success": fmt(low_retry_success[0]) if low_retry_success else "none this week",
        "partial_needing_review": fmt(partials[0]) if partials else (fmt(needs[0]) if needs else "none this week"),
    }


def dominant_failure_pattern(runs: list) -> str:
    flags = top_flags(runs)
    if flags:
        return flags[0][0].replace("_", " ")
    oc = outcome_counts(runs)
    if oc.get("failure", 0) + oc.get("partial", 0) > 0:
        return "outcome failures / partials (root cause not yet categorised)"
    return "no clear failure pattern this week"


def experiment_suggestions(runs: list) -> list[str]:
    flags = top_flags(runs)
    suggestions = []
    flag_to_experiment = {
        "loop_detected": "Add a loop-detection instruction to the system prompt — stop and ask when retry count exceeds 2",
        "prompt_was_ambiguous": "Add a clarification step: agent must restate task as one sentence before acting",
        "insufficient_repo_context": "Pre-warm context with CLAUDE.md or a project brief before starting coding sessions",
        "wrong_tool_chosen": "Review tool selection: add explicit guidance on when to use Bash vs Edit vs Agent",
        "verification_missing": "Add a verification checklist to the session close: run tests, check the thing works",
        "over_engineered": "Constrain scope: add 'do the minimum necessary' instruction to task framing",
        "hallucinated_api_or_function": "Add a 'check it exists before using it' rule to the system prompt",
        "missed_existing_code": "Require a codebase search step before writing new code",
    }
    for flag, run_ids in flags[:2]:
        exp = flag_to_experiment.get(flag)
        if exp:
            suggestions.append(exp)
    if not suggestions:
        suggestions.append("No strong experiment signal this week — continue logging for more data")
    return suggestions


# ── scorecard renderer ────────────────────────────────────────────────────────

def render_scorecard(week_label: str, runs: list, prev_runs: list, date_range: tuple) -> str:
    total = len(runs)
    prev_total = len(prev_runs)
    oc = outcome_counts(runs)
    prev_oc = outcome_counts(prev_runs)

    def trend(curr_n, prev_n, total_c, total_p):
        if total_p == 0 or total_c == 0:
            return "n/a"
        curr_pct = curr_n / total_c * 100
        prev_pct = prev_n / total_p * 100
        delta = curr_pct - prev_pct
        if abs(delta) < 5:
            return "→ flat"
        return f"↑ +{delta:.0f}pp" if delta > 0 else f"↓ {delta:.0f}pp"

    projects = by_project(runs)
    task_types = by_task_type(runs)
    flags = top_flags(runs)
    inspect = runs_to_inspect(runs)
    experiments = experiment_suggestions(runs)

    proj_rows = "\n".join(
        f"| {p['project']} | {p['runs']} | {p['success_rate']} | {p['needs_review']} | {p['median_retries']} |  |"
        for p in projects
    ) or "| — | — | — | — | — | — |"

    task_rows = "\n".join(
        f"| {t['type']} | {t['runs']} | {t['success_rate']} | {t['needs_review']} | {t['median_retries']} |  |"
        for t in task_types
    )

    flag_rows = "\n".join(
        f"| {flag.replace('_',' ').capitalize()} | {len(ids)} | {', '.join(ids[:3])} |  |  |"
        for flag, ids in flags[:5]
    ) or "| No flags recorded this week | — | — | — | — |"

    needs_review_count = sum(1 for r in runs if r.get("needs_review") == "yes")

    return f"""# Agent Weekly Scorecard — {week_label}

## Week of

- Date range: {date_range[0]} to {date_range[1]}
- Prepared by: auto-generated
- Runs included: {total}
- Notes on data quality: Outcomes are inferred unless `outcome_reviewed` is filled. Review flagged rows before retro.
- Baseline or comparison week: {iso_week_label(datetime.now() - timedelta(weeks=1))} ({prev_total} runs)

## Headline metrics

| Metric | Current week | Previous week | Trend | Comment |
| --- | --- | --- | --- | --- |
| Total runs | {total} | {prev_total} | {trend(total, prev_total, total or 1, prev_total or 1)} |  |
| Success rate | {pct(oc.get('success',0), total)} | {pct(prev_oc.get('success',0), prev_total)} | {trend(oc.get('success',0), prev_oc.get('success',0), total, prev_total)} | Inferred unless reviewed |
| Partial rate | {pct(oc.get('partial',0), total)} | {pct(prev_oc.get('partial',0), prev_total)} | {trend(oc.get('partial',0), prev_oc.get('partial',0), total, prev_total)} | Inferred unless reviewed |
| Failure rate | {pct(oc.get('failure',0), total)} | {pct(prev_oc.get('failure',0), prev_total)} | {trend(oc.get('failure',0), prev_oc.get('failure',0), total, prev_total)} | Inferred unless reviewed |
| Needs-review rate | {pct(needs_review_count, total)} | n/a | n/a |  |
| Acceptance without edit rate | {acceptance_rate(runs)} | n/a | n/a | Reviewed subset only unless explicitly inferred |
| Median retry count | {median_retries(runs)} | {median_retries(prev_runs)} | n/a |  |
| Loop-detected rate | {flag_rate(runs, 'loop_detected')} | n/a | n/a |  |
| Median total duration | {median_duration(runs)} | {median_duration(prev_runs)} | n/a | Multi-day sessions excluded |
| Wrong-tool-chosen rate | {flag_rate(runs, 'wrong_tool_chosen')} | n/a | n/a | Reviewed subset only |
| Verification-missing rate | {flag_rate(runs, 'verification_missing')} | n/a | n/a | Reviewed subset only |

## Interpretation guardrails

- If this is the first tracked week, mark previous week as `n/a` and use comments to capture baseline observations.
- Do not treat movement of fewer than 3 runs as a real trend unless the effect is very large.
- Prefer medians over averages for retries, duration, and token usage.
- If reviewed-run coverage is partial, label reviewer-coded rates as "reviewed subset only".
- Call out explicitly when the scorecard is mostly inference-driven.
- Segment by repo, team, model, or task type before drawing cross-cutting conclusions.

## By project

| Project | Runs | Success rate | Needs review | Median retries | Key note |
| --- | --- | --- | --- | --- | --- |
{proj_rows}

## By task type

| Task type | Runs | Success rate | Needs review | Median retries | Key note |
| --- | --- | --- | --- | --- | --- |
{task_rows}

## Top positive signals

_(fill during retro — look for low-retry successes and accepted-without-edit runs)_

## Top failure patterns

| Pattern | Count | Example run_ids | Likely category | Comment |
| --- | --- | --- | --- | --- |
{flag_rows}

## Runs to inspect in retro

- Best run to learn from: {inspect['best_win']}
- Most damaging failure: {inspect['worst_failure']}
- Clean success with low retries: {inspect['clean_success']}
- Partial or uncertain run needing review: {inspect['partial_needing_review']}

## Recommended focus for retro

- Primary question: What drove the {pct(oc.get('failure',0) + oc.get('partial',0) + oc.get('uncertain',0), total)} non-success rate this week?
- Candidate experiment: {experiments[0]}
- Metric to watch next: success rate and median retry count
- Team, repo, or workflow slice to inspect next: {projects[0]['project'] if projects else 'n/a'}
"""


# ── retro renderer ────────────────────────────────────────────────────────────

def render_retro(week_label: str, runs: list, date_range: tuple, scorecard_path: str) -> str:
    total = len(runs)
    oc = outcome_counts(runs)
    needs_review = [r for r in runs if r.get("needs_review") == "yes"]
    flags = top_flags(runs)
    experiments = experiment_suggestions(runs)
    inspect = runs_to_inspect(runs)
    dominant = dominant_failure_pattern(runs)

    most_common_task = Counter(r.get("task_type_inferred", "other") for r in runs).most_common(1)
    most_common_task_str = most_common_task[0][0] if most_common_task else "n/a"

    projects_str = ", ".join(set(r.get("team_or_repo", "") for r in runs if r.get("team_or_repo"))) or "n/a"

    # Sessions needing review — formatted as a bullet list
    review_bullets = "\n".join(
        f"- `{r['run_id']}` — {r.get('task_title','')[:60]} (outcome: {r.get('outcome_inferred','?')})"
        for r in needs_review[:8]
    ) or "- None flagged this week"

    # Root cause grouping from flags
    root_cause_groups = defaultdict(list)
    flag_to_category = {
        "prompt_was_ambiguous": "prompt",
        "acceptance_criteria_unclear": "task_framing",
        "user_request_needed_clarification": "task_framing",
        "insufficient_repo_context": "context",
        "wrong_tool_chosen": "tool",
        "unnecessary_steps": "reasoning",
        "missed_existing_code": "context",
        "over_engineered": "reasoning",
        "hallucinated_api_or_function": "reasoning",
        "correct_but_slow": "workflow",
        "verification_missing": "workflow",
        "loop_detected": "workflow",
    }
    for flag, run_ids in flags:
        cat = flag_to_category.get(flag, "mixed")
        root_cause_groups[cat].extend(run_ids)

    root_cause_summary = "\n".join(
        f"- **{cat}**: {len(ids)} run(s) — flags: {', '.join(f for f, rids in flags if flag_to_category.get(f) == cat)}"
        for cat, ids in sorted(root_cause_groups.items(), key=lambda x: -len(x[1]))
    ) or "- No flags recorded — root causes not yet categorised. Fill `root_cause_category` during review."

    exp_rows = "\n".join(
        f"| {exp[:60]} |  |  |  | success rate, retry count |  |"
        for exp in experiments[:2]
    )

    return f"""# Agent Weekly Retrospective — {week_label}

## Session details

- Date: {date_range[1]} (end of week)
- Facilitator:
- Participants:
- Run range reviewed: {date_range[0]} to {date_range[1]}
- Scorecard reference: {scorecard_path}
- Previous experiment review:

## 1. Sprint summary

- Total runs analysed: {total}
- Success rate: {pct(oc.get('success',0), total)} (inferred)
- Partial rate: {pct(oc.get('partial',0), total)} (inferred)
- Failure rate: {pct(oc.get('failure',0), total)} (inferred)
- Needs-review rate: {pct(len(needs_review), total)}
- Acceptance without edit rate: {acceptance_rate(runs)}
- Median retry count: {median_retries(runs)}
- Most common task type: {most_common_task_str}
- Projects represented: {projects_str}
- Most common failure mode: {dominant}

## 2. Sessions flagged for review

Inspect these before the retro:

{review_bullets}

## 3. Root cause grouping (pre-populated from flags)

{root_cause_summary}

## 4. What worked well

_(fill during retro — look for low-retry successes and accepted-without-edit runs)_

Best candidate to study: {inspect['best_win']}

- What the agent or operator did:
- Which run_ids demonstrate it:
- Why it contributed to success:

## 5. What caused failures or costly success

_(fill during retro — focus on the dominant pattern: **{dominant}**)_

Most damaging failure: {inspect['worst_failure']}

- What went wrong:
- Which run_ids demonstrate it:
- Whether the issue is inferred or confirmed in review:
- Primary category: _(prompt / task_framing / context / tool / workflow / reasoning / environment)_

## 6. Root cause deep dive

Choose the single most damaging repeated pattern and run 5 Whys.

Pattern: **{dominant}**

- Why did this happen?
- Why did that happen?
- Why did that happen?
- Why did that happen?
- Why did that happen?

Root cause statement:

- Root cause in one sentence:
- Primary category:

## 7. Start / Stop / Continue

### Start

-
-

### Stop

-
-

### Continue

-
-

## 8. Experiment decisions

Select no more than 1-2 experiments. Pre-filled from flag analysis:

| Experiment | Hypothesis | Owner | Start date | Metric to watch | Review date |
| --- | --- | --- | --- | --- | --- |
{exp_rows if exp_rows else '|  |  |  |  | success rate, retry count |  |'}

## 9. Actions agreed

| Action | Type | Owner | Due date | Status |
| --- | --- | --- | --- | --- |
|  | Prompt |  |  |  |
|  | Workflow |  |  |  |

## 10. Watch items

Patterns seen in only one run or where evidence is still weak:

-

## 11. Cadence check

- Did we review the scorecard this week?
- Did we inspect at least 2 supporting runs for each repeated pattern?
- Did we leave with only 1-2 experiments?
- Is any logging field too costly to maintain?

## 12. Decision log entry

- Decision:
- Why:
- Evidence:
- Revisit date:

## Facilitation guardrails

- Do not recommend changes based on only one run
- Treat inference as provisional until a human review confirms or corrects it
- Treat accepted_without_edit=uncertain with outcome=success as partial value, not clean success
- Separate prompt issues from context, tooling, workflow, reasoning, and environment issues
- Prefer small reversible changes
"""


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now(tz=timezone.utc)

    if len(sys.argv) > 1:
        year, week = parse_week_arg(sys.argv[1])
    else:
        iso = now.isocalendar()
        year, week = iso[0], iso[1]

    week_label = f"{year}-W{week:02d}"
    prev_iso = (datetime.fromisocalendar(year, week, 1) - timedelta(weeks=1)).isocalendar()
    prev_label = f"{prev_iso[0]}-W{prev_iso[1]:02d}"
    date_range = week_date_range(year, week)

    current_runs, prev_runs = load_runs(week_label, prev_label)

    if not current_runs:
        print(f"No runs found for {week_label}. Check that run-log.csv has rows with captured_at in this week.")
        print(f"(Found {prev_runs.__len__()} rows in previous week {prev_label})")
        # Generate docs anyway with empty data so files exist
        print("Generating empty-week documents anyway...")

    SCORECARDS_DIR.mkdir(exist_ok=True)
    RETROS_DIR.mkdir(exist_ok=True)

    scorecard_file = SCORECARDS_DIR / f"scorecard-{week_label}.md"
    retro_file = RETROS_DIR / f"retro-{week_label}.md"

    scorecard_content = render_scorecard(week_label, current_runs, prev_runs, date_range)
    retro_content = render_retro(week_label, current_runs, date_range, str(scorecard_file))

    scorecard_file.write_text(scorecard_content)
    retro_file.write_text(retro_content)

    print(f"✓ Scorecard: {scorecard_file}")
    print(f"✓ Retro doc: {retro_file}")
    print(f"  {len(current_runs)} runs this week | {len(prev_runs)} runs last week")


if __name__ == "__main__":
    main()
