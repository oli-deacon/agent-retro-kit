#!/usr/bin/env python3
"""Run the complete no-touch retro pipeline and refresh its visual dashboard."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

from retro_core import (
    KIT_DIR,
    evaluate_experiments,
    load_experiments,
    load_exposures,
    load_runs,
    previous_week,
    resolve_week,
    summarize,
    validate_runs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", default="latest-complete", help="YYYY-Www or latest-complete")
    parser.add_argument("--preserve", action="store_true", help="Do not replace existing generated weekly docs")
    args = parser.parse_args()

    rows = load_runs()
    week = resolve_week(args.week, rows)
    command = [sys.executable, str(KIT_DIR / "scripts" / "generate-weekly-docs.py"), week]
    if not args.preserve:
        command.append("--force")
    subprocess.run(command, check=True)
    subprocess.run([sys.executable, str(KIT_DIR / "scripts" / "generate-dashboard.py")], check=True)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "week": week,
        "current": summarize(rows, week),
        "previous": summarize(rows, previous_week(week)),
        "data_quality": validate_runs(rows),
        "experiments": evaluate_experiments(load_experiments(), load_exposures(), rows),
    }
    snapshot_path = KIT_DIR / "output" / "retro-snapshots" / f"{week}.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")

    print(f"Retro complete: {week}")
    print(f"Snapshot: {snapshot_path}")
    print(f"Data quality: {snapshot['data_quality']['status']}")


if __name__ == "__main__":
    main()
