#!/usr/bin/env python3
"""Record an explicit experiment exposure for a run."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone

from retro_core import EXPOSURES_FILE, load_experiments, load_exposures, load_runs


FIELDS = ["experiment_id", "run_id", "variant", "exposed_at", "source", "note"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment_id")
    parser.add_argument("run_id")
    parser.add_argument("--variant", default="treatment")
    parser.add_argument("--source", default="collector")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    known_experiments = {experiment.get("id") for experiment in load_experiments()}
    if args.experiment_id not in known_experiments:
        raise SystemExit(f"Unknown experiment: {args.experiment_id}")
    known_runs = {row.get("run_id") for row in load_runs()}
    if args.run_id not in known_runs:
        raise SystemExit(f"Unknown run: {args.run_id}")
    if any(
        row.get("experiment_id") == args.experiment_id
        and row.get("run_id") == args.run_id
        and row.get("variant") == args.variant
        for row in load_exposures()
    ):
        print("Exposure already recorded; no change.")
        return

    EXPOSURES_FILE.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not EXPOSURES_FILE.exists() or EXPOSURES_FILE.stat().st_size == 0
    with EXPOSURES_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(
            {
                "experiment_id": args.experiment_id,
                "run_id": args.run_id,
                "variant": args.variant,
                "exposed_at": datetime.now(timezone.utc).isoformat(),
                "source": args.source,
                "note": args.note,
            }
        )
    print(f"Recorded {args.experiment_id}/{args.variant} for {args.run_id}")


if __name__ == "__main__":
    main()
