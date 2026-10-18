import contextlib
import io
import json
import unittest

from activity_monitor.cli import main
from monitoramento.summary import summarize as legacy_summarize
from activity_monitor.summary import summarize


class CliTests(unittest.TestCase):
    def test_demo_outputs_synthetic_english_totals(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main(["--demo"])
        self.assertEqual(json.loads(output.getvalue()), {
            "demo": True, "active_seconds": {"Editor": 120, "Browser": 60}
        })

    def test_default_invocation_explains_available_features(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main([])
        self.assertIn("--demo", output.getvalue())
        self.assertIn("collection is not available yet", output.getvalue())

    def test_legacy_import_uses_the_canonical_core(self):
        self.assertIs(legacy_summarize, summarize)
