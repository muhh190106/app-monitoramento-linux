import unittest

from activity_monitor.summary import summarize


class SummaryTests(unittest.TestCase):
    def test_combines_active_intervals_and_excludes_afk(self):
        events = [
            {"app": "Editor", "seconds": 60, "afk": False},
            {"app": "Editor", "seconds": 30, "afk": False},
            {"app": "Editor", "seconds": 120, "afk": True},
            {"app": "Browser", "seconds": 15, "afk": False},
        ]
        self.assertEqual(summarize(events), {"Editor": 90, "Browser": 15})

    def test_empty(self):
        self.assertEqual(summarize([]), {})

    def test_rejects_invalid_durations(self):
        for seconds in (-1, float("nan"), float("inf"), True, "60"):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                summarize([{"app": "Editor", "seconds": seconds, "afk": False}])

    def test_rejects_ambiguous_afk(self):
        with self.assertRaises(ValueError):
            summarize([{"app": "Editor", "seconds": 10, "afk": "false"}])

    def test_rejects_empty_application_names(self):
        for app in ("", " ", None):
            with self.subTest(app=app), self.assertRaises(ValueError):
                summarize([{"app": app, "seconds": 10, "afk": False}])

    def test_preserves_fractional_seconds(self):
        events = [{"app": "Editor", "seconds": 0.25, "afk": False}] * 2
        self.assertEqual(summarize(events), {"Editor": 0.5})

    def test_rejects_overflowing_totals(self):
        events = [{"app": "Editor", "seconds": 1e308, "afk": False}] * 2
        with self.assertRaises(ValueError):
            summarize(events)
