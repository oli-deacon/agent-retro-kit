#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Generate pre-populated scorecard and retro from run-log.csv
echo "Generating pre-populated docs from run-log.csv..."
if [ -n "${1:-}" ]; then
  python3 "$SCRIPT_DIR/generate-weekly-docs.py" "$1"
else
  python3 "$SCRIPT_DIR/generate-weekly-docs.py"
fi
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_TEMPLATE="$ROOT_DIR/templates/weekly-scorecard-template.md"
RETRO_TEMPLATE="$ROOT_DIR/templates/weekly-retro-template.md"
EXPERIMENT_TEMPLATE="$ROOT_DIR/templates/experiment-backlog-template.md"
DECISION_TEMPLATE="$ROOT_DIR/templates/decision-log-template.md"
SCORECARD_DIR="$ROOT_DIR/scorecards"
RETRO_DIR="$ROOT_DIR/retros"
EXPERIMENT_FILE="$ROOT_DIR/experiment-backlog.md"
DECISION_FILE="$ROOT_DIR/decision-log.md"

week_label="${1:-}"

python3 - "$ROOT_DIR" "$week_label" "$SCORECARD_TEMPLATE" "$RETRO_TEMPLATE" "$EXPERIMENT_TEMPLATE" "$DECISION_TEMPLATE" "$SCORECARD_DIR" "$RETRO_DIR" "$EXPERIMENT_FILE" "$DECISION_FILE" <<'PY'
from __future__ import annotations

import re
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def week_details(label: str | None) -> tuple[str, date, date, date]:
    today = date.today()
    if label:
        match = re.fullmatch(r"(\d{4})-W(\d{2})", label)
        if not match:
            raise SystemExit("Week label must look like YYYY-Www, for example 2026-W26")
        year = int(match.group(1))
        week = int(match.group(2))
        monday = date.fromisocalendar(year, week, 1)
    else:
        iso = today.isocalendar()
        monday = date.fromisocalendar(iso.year, iso.week, 1)

    sunday = monday + timedelta(days=6)
    label_value = f"{monday.isocalendar().year}-W{monday.isocalendar().week:02d}"
    return label_value, monday, sunday, today


def ensure_seed_file(target: Path, template: Path) -> None:
    if target.exists():
        return
    shutil.copyfile(template, target)


def build_scorecard(template_text: str, week_label: str, monday: date, sunday: date, today: date) -> str:
    text = template_text.replace("# Agent Weekly Scorecard Template", f"# {week_label} Weekly Scorecard", 1)
    text = text.replace("- Date range:", f"- Date range: {monday.isoformat()} to {sunday.isoformat()}", 1)
    text = text.replace("- Prepared by:", "- Prepared by: ", 1)
    text = text.replace("- Runs included:", "- Runs included: ", 1)
    text = text.replace("- Notes on data quality:", "- Notes on data quality: ", 1)
    text = text.replace("- Baseline or comparison week:", "- Baseline or comparison week: ", 1)
    return text


def build_retro(template_text: str, week_label: str, today: date) -> str:
    text = template_text.replace("# Agent Weekly Retrospective Template", f"# {week_label} Weekly Retro", 1)
    text = text.replace("- Date:", f"- Date: {today.isoformat()}", 1)
    text = text.replace("- Facilitator:", "- Facilitator: ", 1)
    text = text.replace("- Participants:", "- Participants: ", 1)
    text = text.replace("- Run range reviewed:", "- Run range reviewed: ", 1)
    text = text.replace("- Scorecard reference:", f"- Scorecard reference: `scorecards/{week_label}-scorecard.md`", 1)
    text = text.replace("- Previous experiment review:", "- Previous experiment review: ", 1)
    return text


root_dir = Path(sys.argv[1])
week_label_arg = sys.argv[2] or None
scorecard_template = Path(sys.argv[3])
retro_template = Path(sys.argv[4])
experiment_template = Path(sys.argv[5])
decision_template = Path(sys.argv[6])
scorecard_dir = Path(sys.argv[7])
retro_dir = Path(sys.argv[8])
experiment_file = Path(sys.argv[9])
decision_file = Path(sys.argv[10])

week_label_value, monday_value, sunday_value, today_value = week_details(week_label_arg)

scorecard_dir.mkdir(parents=True, exist_ok=True)
retro_dir.mkdir(parents=True, exist_ok=True)

scorecard_path = scorecard_dir / f"{week_label_value}-scorecard.md"
retro_path = retro_dir / f"{week_label_value}-retro.md"

if not scorecard_path.exists():
    scorecard_path.write_text(
        build_scorecard(scorecard_template.read_text(), week_label_value, monday_value, sunday_value, today_value),
        encoding="utf-8",
    )

if not retro_path.exists():
    retro_path.write_text(
        build_retro(retro_template.read_text(), week_label_value, today_value),
        encoding="utf-8",
    )

ensure_seed_file(experiment_file, experiment_template)
ensure_seed_file(decision_file, decision_template)

print(f"Seeded week: {week_label_value}")
print(f"Scorecard: {scorecard_path.relative_to(root_dir)}")
print(f"Retro: {retro_path.relative_to(root_dir)}")
print(f"Experiment backlog: {experiment_file.relative_to(root_dir)}")
print(f"Decision log: {decision_file.relative_to(root_dir)}")
PY
