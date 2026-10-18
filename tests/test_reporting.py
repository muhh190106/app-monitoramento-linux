from datetime import date, datetime, timedelta
import unittest

try:
    from activity_monitor.reporting import UsageInterval, build_report, demo_intervals
except ImportError:
    raise unittest.SkipTest("Install the desktop extra to run reporting checks")


class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.day = date(2026, 10, 18)

    def interval(self, app, start, end, idle=False):
        return UsageInterval(app, datetime.fromisoformat(start), datetime.fromisoformat(end), idle)

    def test_splits_at_hour_and_excludes_idle_from_application_totals(self):
        events = [self.interval("Editor", "2026-10-18T09:30", "2026-10-18T10:30"),
                  self.interval("Browser", "2026-10-18T10:30", "2026-10-18T10:45", True)]
        report = build_report(events, self.day)
        self.assertEqual(report.active_seconds, 3600)
        self.assertEqual(report.idle_seconds, 900)
        self.assertEqual([app.app for app in report.applications], ["Editor"])
        self.assertEqual(report.timeline[9].active_seconds, 1800)
        self.assertEqual(report.timeline[10].active_seconds, 1800)
        self.assertEqual(report.timeline[10].idle_seconds, 900)

    def test_clips_intervals_to_day_boundaries(self):
        event = self.interval("Editor", "2026-10-17T23:30", "2026-10-18T00:30")
        self.assertEqual(build_report([event], self.day).active_seconds, 1800)

    def test_week_splits_midnight_without_losing_time(self):
        event = self.interval("Editor", "2026-10-17T23:30", "2026-10-18T00:30")
        report = build_report([event], self.day, 7)
        self.assertEqual(report.active_seconds, 3600)
        self.assertEqual(report.timeline[-2].active_seconds, 1800)
        self.assertEqual(report.timeline[-1].active_seconds, 1800)

    def test_application_filter_recomputes_totals_and_shares(self):
        events = [self.interval("Editor", "2026-10-18T09:00", "2026-10-18T10:00"),
                  self.interval("Browser", "2026-10-18T10:00", "2026-10-18T10:30")]
        report = build_report(events, self.day, application="Browser")
        self.assertEqual(report.active_seconds, 1800)
        self.assertEqual(report.applications[0].share, 1)

    def test_rejects_overlapping_intervals(self):
        events = [self.interval("A", "2026-10-18T09:00", "2026-10-18T10:00"),
                  self.interval("B", "2026-10-18T09:59", "2026-10-18T10:30")]
        with self.assertRaises(ValueError):
            build_report(events, self.day)

    def test_empty_period_has_complete_zero_timeline(self):
        report = build_report(demo_intervals(self.day), self.day - timedelta(days=60), 30)
        self.assertEqual(report.active_seconds, 0)
        self.assertEqual(report.applications, ())
        self.assertEqual(len(report.timeline), 30)

    def test_idle_only_period_has_no_application_ranking(self):
        event = self.interval("Editor", "2026-10-18T09:00", "2026-10-18T09:30", True)
        report = build_report([event], self.day)
        self.assertEqual(report.active_seconds, 0)
        self.assertEqual(report.idle_seconds, 1800)
        self.assertEqual(report.applications, ())

    def test_period_windows_are_inclusive_of_reference_day(self):
        for days in (1, 7, 30):
            with self.subTest(days=days):
                report = build_report(demo_intervals(self.day), self.day, days)
                self.assertEqual(report.start, self.day - timedelta(days=days - 1))
                self.assertEqual(report.end, self.day)
                self.assertAlmostEqual(sum(p.active_seconds for p in report.timeline), report.active_seconds)
                self.assertAlmostEqual(sum(a.share for a in report.applications), 1)

    def test_rejects_invalid_periods_and_boundaries(self):
        for days in (0, 2, True, 1.0):
            with self.subTest(days=days), self.assertRaises(ValueError):
                build_report([], self.day, days)
        with self.assertRaises(ValueError):
            build_report([], date.min, 30)

    def test_demo_totals_and_determinism(self):
        samples = demo_intervals(self.day)
        self.assertEqual(samples, demo_intervals(self.day))
        report = build_report(samples, self.day)
        self.assertEqual(report.active_seconds, 345 * 60)
        self.assertEqual(report.idle_seconds, 20 * 60)
        self.assertEqual(report.applications[0].app, "Editor")

    def test_interval_validation(self):
        point = datetime(2026, 10, 18, 9)
        for arguments in (("", point, point + timedelta(minutes=1), False),
                          ("Editor", point, point, False),
                          ("Editor", point, point + timedelta(minutes=1), "false")):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                UsageInterval(*arguments)
