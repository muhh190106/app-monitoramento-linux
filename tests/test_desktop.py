"""Run with STIME_DESKTOP_TESTS=1 in a graphical session or under Xvfb."""

from datetime import date, timedelta
import os
import unittest


@unittest.skipUnless(os.environ.get("STIME_DESKTOP_TESTS") == "1", "Desktop smoke tests need a display and desktop dependencies")
class DesktopTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        from activity_monitor.desktop import Dashboard
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = Dashboard(self.root, anchor=date(2026, 10, 18))
        self.root.update_idletasks()

    def tearDown(self):
        self.root.destroy()

    def test_filters_language_and_empty_state(self):
        self.assertEqual(self.app.metrics["active"].get(), "5h 45m")
        self.app.set_period(7)
        self.assertGreater(self.app.report.active_seconds, 345 * 60)
        self.app.set_application("Browser")
        self.assertEqual(len(self.app.report.applications), 1)
        self.app.set_language("pt-BR")
        self.assertEqual(self.app.title_label.cget("text"), "Visão geral")
        self.assertEqual(self.app.days, 7)
        self.assertEqual(self.app.application, "Browser")
        self.app.reference = self.app.anchor - timedelta(days=60)
        self.app.refresh()
        self.assertEqual(self.app.metrics["active"].get(), "0s")
        self.assertEqual(len(self.app.table.get_children()), 0)
        self.assertIn("Sem atividade", self.app.empty_label.cget("text"))
        self.app.reset_filters()
        self.assertEqual(self.app.metrics["active"].get(), "5h 45m")

    def test_invalid_date_preserves_previous_view(self):
        previous = self.app.report
        self.app.date_entry.delete(0, "end")
        self.app.date_entry.insert(0, "invalid date")
        self.app.apply_date()
        self.assertEqual(self.app.report, previous)
        self.assertIn("YYYY-MM-DD", self.app.message.get())
