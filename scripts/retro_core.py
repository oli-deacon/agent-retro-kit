#!/usr/bin/env python3
"""Shared, dependency-free analytics for automated agent retros."""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


KIT_DIR = Path(__file__).resolve().parent.parent
RUN_LOG = KIT_DIR / "data" / "run-log.csv"
EXPERIMENTS_FILE = KIT_DIR / "experiments.json"
EXPOSURES_FILE = KIT_DIR / "data" / "experiment-exposures.csv"

OUTCOMES = {"success", "partial", "failure", "abandoned", "uncertain"}
FLAG_TO_ROOT_CAUSE = {
    "prompt_was_ambiguous": "prompt",
    "acceptance_criteria_unclear": "task_framing",
    "user_request_needed_clarification": "task_framing",
    "insufficient_repo_context": "context",
    "missed_existing_code": "context",
    "wrong_tool_chosen": "tool",
    "verification_missing": "workflow",
    "loop_detected": "workflow",
    "correct_but_slow": "workflow",
    "unnecessary_steps": "reasoning",
    "over_engineered": "reasoning",
    "hallucinated_api_or_function": "reasoning",
}


def load_runs(path: Path = RUN_LOG) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_timestamp(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None
    return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc)


def row_datetime(row: dict[str, str]) -> datetime | None:
    return parse_timestamp(row.get("captured_at") or row.get("run_started_at", ""))


def iso_week(value: datetime | date) -> str:
    iso = value.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def row_week(row: dict[str, str]) -> str:
    captured = row_datetime(row)
    return iso_week(captured) if captured else ""


def week_range(label: str) -> tuple[date, date]:
    try:
        year_text, week_text = label.split("-W", maxsplit=1)
        monday = date.fromisocalendar(int(year_text), int(week_text), 1)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid week {label!r}; expected YYYY-Www") from exc
    return monday, monday + timedelta(days=6)


def previous_week(label: str) -> str:
    monday, _ = week_range(label)
    return iso_week(monday - timedelta(days=7))


def resolve_week(requested: str, rows: list[dict[str, str]], today: date | None = None) -> str:
    if requested != "latest-complete":
        week_range(requested)
        return requested
    today = today or date.today()
    current_monday = today - timedelta(days=today.weekday())
    complete = sorted(
        {
            row_week(row)
            for row in rows
            if row_datetime(row) and row_datetime(row).date() < current_monday
        }
    )
    return complete[-1] if complete else iso_week(current_monday - timedelta(days=7))


def effective_outcome(row: dict[str, str]) -> str:
    value = (row.get("outcome_reviewed") or row.get("outcome_inferred") or "uncertain").strip()
    return value if value in OUTCOMES else "uncertain"


def effective_acceptance(row: dict[str, str]) -> str:
    value = row.get("accepted_without_edit_reviewed") or row.get("accepted_without_edit_inferred") or "uncertain"
    return value if value in {"yes", "no", "uncertain"} else "uncertain"


def flags(row: dict[str, str]) -> list[str]:
    return [item.strip() for item in (row.get("flags") or "").split("|") if item.strip()]


def verification_status(row: dict[str, str]) -> str:
    reviewed = (row.get("verification_status_reviewed") or "").strip()
    if reviewed:
        return reviewed
    if "verification_missing" in flags(row):
        return "incomplete"
    if effective_outcome(row) in {"partial", "failure", "abandoned"}:
        return "incomplete"
    evidence = (row.get("tool_summary") or "").lower()
    if effective_outcome(row) == "success" and any(
        token in evidence for token in ("test", "browser", "deploy", "artifact", "check", "verify")
    ):
        return "inferred_completed"
    return "unknown"


def root_cause(row: dict[str, str]) -> str:
    reviewed = (row.get("root_cause_category") or "").strip()
    if reviewed:
        return reviewed
    inferred = [FLAG_TO_ROOT_CAUSE[item] for item in flags(row) if item in FLAG_TO_ROOT_CAUSE]
    if not inferred:
        return "none_signalled" if effective_outcome(row) == "success" else "unclassified"
    return Counter(inferred).most_common(1)[0][0]


def evidence_confidence(row: dict[str, str]) -> str:
    if row.get("outcome_reviewed") and row.get("verification_status_reviewed"):
        return "high"
    if effective_outcome(row) != "uncertain" and verification_status(row) != "unknown":
        return "medium"
    return "low"


def int_value(row: dict[str, str], key: str) -> int | None:
    try:
        return int(row.get(key, ""))
    except (TypeError, ValueError):
        return None


def percent(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator * 100, 1) if denominator else None


def summarize(rows: list[dict[str, str]], week: str | None = None) -> dict[str, Any]:
    selected = [row for row in rows if not week or row_week(row) == week]
    outcomes = Counter(effective_outcome(row) for row in selected)
    retries = [value for row in selected if (value := int_value(row, "retry_count_inferred")) is not None]
    durations = [
        value
        for row in selected
        if (value := int_value(row, "duration_minutes_inferred")) is not None and 0 < value < 1440
    ]
    verified = sum(verification_status(row) in {"completed", "not_needed", "inferred_completed"} for row in selected)
    accepted_known = [row for row in selected if effective_acceptance(row) in {"yes", "no"}]
    accepted = sum(effective_acceptance(row) == "yes" for row in accepted_known)
    root_causes = Counter(root_cause(row) for row in selected if root_cause(row) not in {"none_signalled"})
    all_flags = Counter(item for row in selected for item in flags(row))
    confidence = Counter(evidence_confidence(row) for row in selected)
    return {
        "week": week,
        "runs": len(selected),
        "outcomes": dict(outcomes),
        "success_rate": percent(outcomes["success"], len(selected)),
        "non_success_rate": percent(len(selected) - outcomes["success"], len(selected)),
        "acceptance_without_edit_rate": percent(accepted, len(accepted_known)),
        "verification_completed_rate": percent(verified, len(selected)),
        "median_retries": statistics.median(retries) if retries else None,
        "median_duration_minutes": statistics.median(durations) if durations else None,
        "needs_review": sum((row.get("needs_review") or "").lower() == "yes" for row in selected),
        "root_causes": dict(root_causes.most_common()),
        "flags": dict(all_flags.most_common()),
        "confidence": dict(confidence),
    }


def weekly_summaries(rows: list[dict[str, str]], limit: int = 12) -> list[dict[str, Any]]:
    weeks = sorted({row_week(row) for row in rows if row_week(row)})[-limit:]
    return [summarize(rows, week) for week in weeks]


def validate_runs(rows: list[dict[str, str]]) -> dict[str, Any]:
    ids = [row.get("run_id", "").strip() for row in rows]
    duplicates = sorted(run_id for run_id, count in Counter(ids).items() if run_id and count > 1)
    issues: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=2):
        if not row.get("run_id", "").strip():
            issues.append({"row": str(index), "issue": "missing_run_id"})
        if not row_datetime(row):
            issues.append({"row": str(index), "issue": "invalid_captured_at"})
        inferred = (row.get("outcome_inferred") or "").strip()
        if inferred and inferred not in OUTCOMES:
            issues.append({"row": str(index), "issue": "invalid_outcome"})
    newest = max((row_datetime(row) for row in rows if row_datetime(row)), default=None)
    stale_days = (datetime.now(tz=newest.tzinfo) - newest).days if newest else None
    status = "ready"
    if issues or duplicates:
        status = "needs_attention"
    elif not rows or (stale_days is not None and stale_days > 14):
        status = "partial"
    return {
        "status": status,
        "rows": len(rows),
        "duplicate_run_ids": duplicates,
        "issues": issues,
        "newest_capture": newest.isoformat() if newest else None,
        "stale_days": stale_days,
    }


def load_experiments(path: Path = EXPERIMENTS_FILE) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("experiments", [])


def load_exposures(path: Path = EXPOSURES_FILE) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def evaluate_experiments(
    experiments: Iterable[dict[str, Any]],
    exposures: list[dict[str, str]],
    runs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    run_by_id = {row.get("run_id"): row for row in runs if row.get("run_id")}
    result = []
    for experiment in experiments:
        exp_id = experiment.get("id", "")
        exp_exposures = [row for row in exposures if row.get("experiment_id") == exp_id]
        variants: dict[str, list[dict[str, str]]] = defaultdict(list)
        missing_runs = 0
        for exposure in exp_exposures:
            run = run_by_id.get(exposure.get("run_id"))
            if run:
                variants[exposure.get("variant") or "treatment"].append(run)
            else:
                missing_runs += 1
        variant_metrics = {
            name: {
                "exposures": len(variant_runs),
                "success_rate": summarize(variant_runs)["success_rate"],
                "verification_completed_rate": summarize(variant_runs)["verification_completed_rate"],
                "median_retries": summarize(variant_runs)["median_retries"],
            }
            for name, variant_runs in sorted(variants.items())
        }
        minimum = int(experiment.get("minimum_exposures", 5))
        status = experiment.get("status", "proposed")
        if status == "active" and not exp_exposures:
            status = "instrumentation_incomplete"
        elif status == "active" and len(exp_exposures) < minimum:
            status = "collecting"
        result.append(
            {
                **experiment,
                "evaluation_status": status,
                "explicit_exposures": len(exp_exposures),
                "missing_run_refs": missing_runs,
                "variant_metrics": variant_metrics,
            }
        )
    return result
