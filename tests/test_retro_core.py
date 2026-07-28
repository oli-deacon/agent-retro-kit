from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from retro_core import (  # noqa: E402
    evaluate_experiments,
    evidence_confidence,
    resolve_week,
    summarize,
    validate_runs,
    verification_status,
)


def run(run_id: str, captured_at: str, **changes: str) -> dict[str, str]:
    row = {
        "run_id": run_id,
        "captured_at": captured_at,
        "outcome_inferred": "success",
        "accepted_without_edit_inferred": "yes",
        "retry_count_inferred": "1",
        "duration_minutes_inferred": "15",
        "tool_summary": "edit|tests",
        "needs_review": "no",
        "flags": "",
    }
    row.update(changes)
    return row


class RetroCoreTests(unittest.TestCase):
    def test_latest_complete_ignores_current_week(self) -> None:
        rows = [
            run("old", "2026-07-22T10:00:00+00:00"),
            run("current", "2026-07-28T10:00:00+00:00"),
        ]
        self.assertEqual(resolve_week("latest-complete", rows, date(2026, 7, 28)), "2026-W30")

    def test_summary_uses_reviewed_outcome_and_verification(self) -> None:
        rows = [
            run(
                "one",
                "2026-07-22T10:00:00+00:00",
                outcome_inferred="success",
                outcome_reviewed="partial",
                verification_status_reviewed="blocked",
            ),
            run("two", "2026-07-23T10:00:00+00:00"),
        ]
        result = summarize(rows, "2026-W30")
        self.assertEqual(result["success_rate"], 50.0)
        self.assertEqual(result["verification_completed_rate"], 50.0)
        self.assertEqual(result["outcomes"], {"partial": 1, "success": 1})

    def test_confidence_requires_outcome_and_verification_review(self) -> None:
        reviewed = run(
            "reviewed",
            "2026-07-22T10:00:00+00:00",
            outcome_reviewed="success",
            verification_status_reviewed="completed",
        )
        self.assertEqual(evidence_confidence(reviewed), "high")
        self.assertEqual(verification_status(run("inferred", "2026-07-22T10:00:00+00:00")), "inferred_completed")

    def test_validation_reports_duplicates_and_bad_dates(self) -> None:
        rows = [run("duplicate", "not-a-date"), run("duplicate", "2026-07-22T10:00:00+00:00")]
        quality = validate_runs(rows)
        self.assertEqual(quality["status"], "needs_attention")
        self.assertEqual(quality["duplicate_run_ids"], ["duplicate"])
        self.assertIn({"row": "2", "issue": "invalid_captured_at"}, quality["issues"])

    def test_experiments_count_only_explicit_exposures(self) -> None:
        runs = [run("treated", "2026-07-22T10:00:00+00:00"), run("unlinked", "2026-07-22T11:00:00+00:00")]
        experiments = [{"id": "EXP-1", "title": "Test", "status": "active", "minimum_exposures": 2}]
        exposures = [{"experiment_id": "EXP-1", "run_id": "treated", "variant": "treatment"}]
        evaluated = evaluate_experiments(experiments, exposures, runs)[0]
        self.assertEqual(evaluated["explicit_exposures"], 1)
        self.assertEqual(evaluated["evaluation_status"], "collecting")
        self.assertEqual(evaluated["variant_metrics"]["treatment"]["exposures"], 1)

        no_exposures = evaluate_experiments(experiments, [], runs)[0]
        self.assertEqual(no_exposures["evaluation_status"], "instrumentation_incomplete")


if __name__ == "__main__":
    unittest.main()
