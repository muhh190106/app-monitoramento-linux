from datetime import date
import unittest

try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from activity_monitor.charts import draw_timeline
    from activity_monitor.i18n import MESSAGES
    from activity_monitor.reporting import build_report, demo_intervals
except ImportError:
    raise unittest.SkipTest("Install the desktop extra to run chart checks")


class ChartTests(unittest.TestCase):
    def test_chart_totals_match_report_in_both_languages(self):
        anchor = date(2026, 10, 18)
        report = build_report(demo_intervals(anchor), anchor)
        for language in ("en", "pt-BR"):
            with self.subTest(language=language):
                figure = Figure()
                axis = draw_timeline(figure, report, language)
                FigureCanvasAgg(figure).draw()
                self.assertAlmostEqual(sum(patch.get_height() for patch in axis.patches) * 60,
                                       report.active_seconds + report.idle_seconds)
                self.assertEqual(axis.get_ylabel(), MESSAGES[language]["minutes"])

    def test_empty_chart_explains_missing_data(self):
        figure = Figure()
        axis = draw_timeline(figure, build_report([], date(2026, 10, 18)), "pt-BR")
        FigureCanvasAgg(figure).draw()
        self.assertIn("Sem atividade", axis.texts[0].get_text())

    def test_languages_cover_the_same_interface(self):
        self.assertEqual(set(MESSAGES["en"]), set(MESSAGES["pt-BR"]))
