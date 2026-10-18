"""Validate the planned wire contract, without starting a server or collecting data."""

import copy
import json
from pathlib import Path
import unittest

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from openapi_spec_validator import validate
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError:
    raise unittest.SkipTest("Install the contracts extra to validate the API contract")


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "docs/contracts/openapi.json"
        cls.spec = json.loads(path.read_text(encoding="utf-8"))
        cls.registry = Registry().with_resource(
            "urn:stime:api", Resource.from_contents(cls.spec, default_specification=DRAFT202012)
        )

    def validator(self, name):
        return Draft202012Validator(
            {"$ref": f"urn:stime:api#/components/schemas/{name}"},
            registry=self.registry, format_checker=FormatChecker(),
        )

    def batch(self):
        example = self.spec["paths"]["/api/v1/events/batch"]["post"]["requestBody"]["content"]["application/json"]["example"]
        return copy.deepcopy(example)

    def test_openapi_document_is_valid(self):
        validate(self.spec)

    def test_active_idle_and_browser_payloads(self):
        batch = self.batch()
        self.validator("EventBatch").validate(batch)
        event = batch["events"][0]
        event["state"] = "idle"
        del event["app_id"], event["app_name"]
        self.validator("EventBatch").validate(batch)
        batch["source"] = "browser"
        event.update(state="active", app_id="windows:sample-browser.exe",
                     app_name="Sample Browser", domain="study.example")
        self.validator("EventBatch").validate(batch)
        del event["app_id"]
        self.assertFalse(self.validator("EventBatch").is_valid(batch))

    def test_rejects_private_fields_and_wrong_source_shapes(self):
        for fields in ({"url": "https://study.example/private"},
                       {"window_title": "Synthetic title"},
                       {"domain": "study.example"}, {"state": "idle"}):
            with self.subTest(fields=fields):
                batch = self.batch()
                batch["events"][0].update(fields)
                self.assertFalse(self.validator("EventBatch").is_valid(batch))

    def test_rejects_invalid_identifiers_timestamps_and_batch_sizes(self):
        for value in ("2026-10-01T12:00:00", "2026-13-01T12:00:00Z",
                      "2026-10-01T12:00:00+03:00"):
            with self.subTest(timestamp=value):
                batch = self.batch()
                batch["events"][0]["started_at"] = value
                self.assertFalse(self.validator("EventBatch").is_valid(batch))
        batch = self.batch()
        batch["device_id"] = "invalid-id"
        self.assertFalse(self.validator("EventBatch").is_valid(batch))
        for count in (0, 501):
            batch = self.batch()
            batch["events"] *= count
            self.assertFalse(self.validator("EventBatch").is_valid(batch))

    def test_goal_targets_are_exclusive(self):
        for target, fields in (("all", {}), ("application", {"app_id": "linux:org.example.Editor"}),
                               ("domain", {"domain": "study.example"})):
            with self.subTest(target=target):
                goal = dict(device_id=self.batch()["device_id"], target_type=target,
                            period="day", timezone="UTC", limit_seconds=3600, **fields)
                self.validator("GoalInput").validate(goal)
                goal.update(app_id="windows:sample.exe", domain="study.example")
                self.assertFalse(self.validator("GoalInput").is_valid(goal))

    def test_focus_requires_valid_duration_and_distinct_rules(self):
        batch = self.batch()
        focus = dict(device_id=batch["device_id"], duration_seconds=1500,
                     rule_ids=[batch["events"][0]["event_id"]])
        self.validator("FocusInput").validate(focus)
        for fields in ({"duration_seconds": 0}, {"duration_seconds": 14401},
                       {"rule_ids": []}, {"rule_ids": focus["rule_ids"] * 2}):
            with self.subTest(fields=fields):
                self.assertFalse(self.validator("FocusInput").is_valid(dict(focus, **fields)))
