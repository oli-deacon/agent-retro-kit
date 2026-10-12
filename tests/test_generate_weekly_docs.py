import csv
import importlib.util
from pathlib import Path
import tempfile
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'generate-weekly-docs.py'
spec = importlib.util.spec_from_file_location('weekly', SCRIPT)
weekly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weekly)


def run(run_id, retries=None, duration=None, **extra):
    return dict(run_id=run_id, task_title=run_id, outcome_inferred='success',
                retry_count_inferred=retries, duration_minutes_inferred=duration, **extra)


class WeekTests(unittest.TestCase):
    def test_backfill_uses_start_not_capture_or_update(self):
        row = dict(run_started_at='2026-06-28T23:30:00-0700',
                   run_last_updated_at='2026-06-29T10:00:00Z',
                   captured_at='2026-07-07T12:00:00Z')
        self.assertEqual(weekly.captured_week(row), '2026-W26')

    def test_missing_start_uses_legacy_capture(self):
        for start in (None, '', '   '):
            with self.subTest(start=start):
                self.assertEqual(weekly.captured_week(dict(run_started_at=start,
                    captured_at='2026-07-07T12:00:00Z')), '2026-W28')
        self.assertEqual(weekly.captured_week({'captured_at': '2026-07-07T12:00:00Z'}), '2026-W28')

    def test_malformed_start_is_not_reassigned_to_import_week(self):
        for start in ('bad', '2026-02-30T10:00:00Z', '2026-07-07T12:00:00garbage'):
            with self.subTest(start=start):
                self.assertEqual(weekly.captured_week(dict(run_started_at=start,
                    captured_at='2026-07-07T12:00:00Z')), '')
        for row in ({}, {'captured_at': 'bad'}):
            self.assertEqual(weekly.captured_week(row), '')

    def test_iso_year_and_calendar_date(self):
        for stamp in ('2021-01-01T00:10:00+1400', '2021-01-03T23:30:00-1200'):
            self.assertEqual(weekly.captured_week({'run_started_at': stamp}), '2020-W53')

    def test_load_current_and_previous_weeks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'runs.csv'
            with path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['run_id', 'run_started_at', 'captured_at'])
                writer.writeheader()
                writer.writerows([
                    dict(run_id='old', run_started_at='2021-01-03T23:00:00Z', captured_at='2021-02-01T12:00:00Z'),
                    dict(run_id='current', run_started_at='2021-01-04T00:00:00Z', captured_at='2021-02-01T12:00:00Z'),
                    dict(run_id='legacy', captured_at='2021-01-04T12:00:00Z'),
                    dict(run_id='invalid', run_started_at='bad', captured_at='2021-01-04T12:00:00Z'),
                ])
            with patch.object(weekly, 'RUN_LOG', path):
                current, previous = weekly.load_runs('2021-W01', '2020-W53')
            self.assertEqual([r['run_id'] for r in current], ['current', 'legacy'])
            self.assertEqual([r['run_id'] for r in previous], ['old'])


class EvidenceTests(unittest.TestCase):
    def test_unknown_retries_excluded_and_zero_retained(self):
        rows = [{}, *[run(str(i), value) for i, value in enumerate((None, '', ' ', 'bad', '1.5', '-1'))]]
        self.assertEqual(weekly.median_retries(rows), 'n/a')
        self.assertEqual(weekly.median_retries(rows + [run('zero', '0')]), '0')
        self.assertEqual(weekly.median_retries(rows + [run('zero', '0'), run('three', '3')]), '1.5')

    def test_costly_and_clean_selected_separately(self):
        rows = [run('unknown', '', '900'), run('bad', 'oops', '999'),
                run('clean', '0', '10'), run('costly', '4', '60'),
                run('lower-retry', '3', '800'), run('shorter', '4', '20')]
        selected = weekly.runs_to_inspect(rows)
        self.assertIn('`costly`', selected['costly_success'])
        self.assertIn('4 corrective retries; 60 min', selected['costly_success'])
        self.assertIn('`clean`', selected['clean_success'])
        self.assertIn('`clean`', selected['best_win'])

    def test_reviewed_outcomes_take_precedence(self):
        rows = [run('rejected', '99', outcome_reviewed='failure'),
                run('partial', '98', outcome_reviewed='partial'),
                run('uncertain', '97', outcome_reviewed='uncertain'),
                run('confirmed', '2', outcome_reviewed='success')]
        rows[-1]['outcome_inferred'] = 'failure'
        selected = weekly.runs_to_inspect(rows)
        self.assertIn('`confirmed`', selected['costly_success'])
        self.assertIn('`rejected`', selected['worst_failure'])
        self.assertNotIn('`', selected['clean_success'])

    def test_duration_fallback_only_without_measured_success_retries(self):
        rows = [run('short', None, '20'), run('long', 'bad', '80'),
                run('inflated', '', '1440'), run('invalid', '', 'bad'),
                run('zero-duration', '', '0'), run('negative', '', '-10'),
                run('failure', '7', '100', outcome_reviewed='failure')]
        selected = weekly.runs_to_inspect(rows)
        self.assertIn('`long`', selected['costly_success'])
        self.assertIn('duration-only fallback', selected['costly_success'])
        self.assertNotIn('`', selected['clean_success'])
        selected = weekly.runs_to_inspect(rows + [run('measured', '1', '')])
        self.assertIn('`measured`', selected['costly_success'])

    def test_unknown_duration_does_not_win_tie(self):
        rows = [run('multi-day', '4', '1440'), run('missing', '4'), run('usable', '4', '1')]
        self.assertIn('`usable`', weekly.runs_to_inspect(rows)['costly_success'])

    def test_all_unknown_and_empty_evidence(self):
        selected = weekly.runs_to_inspect([run('unknown'), run('malformed', 'bad', 'bad')])
        self.assertIn('unknown', selected['costly_success'])
        self.assertNotIn('`', selected['clean_success'])
        self.assertEqual(weekly.runs_to_inspect([])['costly_success'], 'none this week')

    def test_zero_retries_not_labelled_costly(self):
        selected = weekly.runs_to_inspect([run('zero', '0', '60'), run('unknown', '', '900')])
        self.assertIn('none with positive measured retries', selected['costly_success'])
        self.assertIn('`zero`', selected['clean_success'])

    def test_contrary_edit_evidence_is_not_clean(self):
        for edits in ('no', 'uncertain'):
            with self.subTest(edits=edits):
                selected = weekly.runs_to_inspect([run('edited', '0', accepted_without_edit_inferred=edits)])
                self.assertNotIn('`', selected['clean_success'])
        selected = weekly.runs_to_inspect([run('reviewed', '0',
            accepted_without_edit_inferred='uncertain', accepted_without_edit_reviewed='yes')])
        self.assertIn('`reviewed`', selected['clean_success'])

    def test_both_documents_render_costly_and_clean_evidence(self):
        rows = [run('clean', '0', '10'), run('costly', '3', '90')]
        date_range = weekly.week_date_range(2026, 28)
        docs = [weekly.render_scorecard('2026-W28', rows, [], date_range),
                weekly.render_retro('2026-W28', rows, date_range, 'scorecard.md')]
        for doc in docs:
            self.assertIn('Costly success worth studying: `costly`', doc)
            self.assertIn('Clean success with measured zero retries: `clean`', doc)
            self.assertIn('effort proxy, not monetary cost', doc)


class CommandLineTests(unittest.TestCase):
    def test_generates_both_reports_from_backfilled_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'scripts').mkdir()
            (root / 'data').mkdir()
            script = root / 'scripts' / SCRIPT.name
            shutil.copyfile(SCRIPT, script)
            rows = [run('clean', '0', '10'), run('costly', '4', '60'), run('unknown')]
            for row in rows:
                row.update(run_started_at='2026-07-07T12:00:00Z', captured_at='2026-10-01T12:00:00Z')
            with (root / 'data' / 'run-log.csv').open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            result = subprocess.run([sys.executable, str(script), '2026-W28'],
                                    cwd=tmp, capture_output=True, text=True, check=True)
            self.assertIn('3 runs this week | 0 runs last week', result.stdout)
            scorecard = (root / 'scorecards' / '2026-W28-scorecard.md').read_text()
            retro = (root / 'retros' / '2026-W28-retro.md').read_text()
            self.assertIn('| Median retry count | 2 | n/a |', scorecard)
            self.assertIn('Median retry count: 2', retro)
            for doc in (scorecard, retro):
                self.assertIn('Costly success worth studying: `costly`', doc)
                self.assertIn('Clean success with measured zero retries: `clean`', doc)


if __name__ == '__main__':
    unittest.main()
