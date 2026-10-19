"""Storage integration checks using isolated temporary databases and synthetic data."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from activity_monitor.storage import Database, default_database_path
from activity_monitor.storage.repository import UsageRepository
from activity_monitor.storage.seed import DEVICE_ID, WORKSPACE_ID, seed_demo
from activity_monitor.storage.time import milliseconds, timestamp, zone


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.db = Database(self.path)
        self.addCleanup(self.db.close)
        self.db.migrate()
        self.repo = UsageRepository(self.db)
        self.now = datetime(2026, 10, 1, 13, tzinfo=timezone.utc)
        self.workspace = self.repo.create_workspace("Synthetic workspace", now=self.now)
        self.device = self.repo.create_device(self.workspace, "Synthetic device", "windows", now=self.now)

    def event(self, start="2026-10-01T12:00:00Z", end="2026-10-01T12:01:00Z", *, idle=False, app="editor", domain=None):
        event = dict(event_id=str(uuid4()), started_at=start, ended_at=end, state="idle" if idle else "active")
        if not idle:
            event.update(app_id=f"windows:sample-{app}.exe", app_name=f"Sample {app}")
        if domain:
            event["domain"] = domain
        return event

    def ingest(self, events, source="desktop", **kwargs):
        return self.repo.ingest(self.workspace, self.device, source, events, now=self.now, **kwargs)

    def count(self, table="usage_sessions"):
        return self.db.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def summary(self, **kwargs):
        return self.repo.summary(self.workspace, self.device, date(2026, 10, 1), **kwargs)

    def test_migrations_are_repeatable_and_data_survives_reopen(self):
        self.ingest([self.event()])
        self.assertEqual(self.db.migrate(), 2)
        with Database(self.path) as reopened:
            reopened.migrate()
            result = UsageRepository(reopened).summary(self.workspace, self.device, date(2026, 10, 1))
            self.assertEqual(result["active_seconds"], 60)
            self.assertEqual(reopened.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_upgrade_from_previous_schema_preserves_data(self):
        with Database(Path(self.temp.name) / "old.sqlite3") as db:
            self.assertEqual(db.migrate(target=1), 1)
            UsageRepository(db).create_workspace("Previous schema", now=self.now)
            db.migrate()
            self.assertEqual(db.connection.execute("SELECT name FROM workspaces").fetchone()[0], "Previous schema")
            self.assertEqual(db.connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 2)

    def test_invalid_history_and_foreign_database_are_not_overwritten(self):
        self.db.connection.execute("UPDATE schema_migrations SET checksum='changed' WHERE version=1")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.db.migrate()
        with Database(Path(self.temp.name) / "foreign.sqlite3") as other:
            other.connection.execute("CREATE TABLE personal_data (value TEXT)")
            other.connection.execute("INSERT INTO personal_data VALUES ('Synthetic record')")
            with self.assertRaisesRegex(ValueError, "unrecognized"):
                other.migrate()
            self.assertEqual(other.connection.execute("SELECT value FROM personal_data").fetchone()[0], "Synthetic record")

    def test_failed_upgrade_is_atomic(self):
        with Database(Path(self.temp.name) / "upgrade.sqlite3") as db:
            db.migrate(target=1)
            db.connection.execute("CREATE INDEX usage_period ON usage_sessions(started_at)")
            with self.assertRaises(sqlite3.OperationalError):
                db.migrate()
            self.assertEqual(db.connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 1)
            self.assertIsNone(db.connection.execute("SELECT name FROM sqlite_master WHERE name='devices_workspace'").fetchone())

    def test_identical_retry_is_idempotent_and_changed_content_conflicts(self):
        event = self.event()
        self.assertEqual(self.ingest([event])["accepted_event_ids"], [event["event_id"]])
        self.assertEqual(self.ingest([event])["duplicate_event_ids"], [event["event_id"]])
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.ingest([dict(event, app_name="Changed sample")])
        self.assertEqual(self.count(), 1)

    def test_duplicate_ids_and_overlap_roll_back_entire_batch(self):
        event = self.event()
        for batch in ([event, event], [event, self.event()], [event, dict(self.event(), url="https://study.example")]):
            with self.subTest(batch=batch), self.assertRaises((ValueError, sqlite3.IntegrityError)):
                self.ingest(batch)
            self.assertEqual(self.count(), 0)
            self.assertEqual(self.count("applications"), 0)

    def test_touching_intervals_and_out_of_order_batches_are_allowed(self):
        first = self.event()
        second = self.event("2026-10-01T12:01:00Z", "2026-10-01T12:02:00Z", idle=True)
        self.ingest([second, first])
        result = self.summary()
        self.assertEqual((result["active_seconds"], result["idle_seconds"]), (60, 60))
        self.assertEqual(len(result["timeline"]), 24)

    def test_browser_time_requires_matching_foreground_application(self):
        self.ingest([self.event(), self.event("2026-10-01T12:01:00Z", "2026-10-01T12:02:00Z", app="browser")])
        events = [self.event(app="browser", domain="study.example"),
                  self.event("2026-10-01T12:01:00Z", "2026-10-01T12:02:00Z", app="browser", domain="study.example")]
        self.ingest(events, "browser", browser_app_id="windows:sample-browser.exe")
        apps, domains = self.summary(), self.summary(dimension="domain")
        self.assertEqual(apps["active_seconds"], 120)
        self.assertEqual(domains["active_seconds"], 60)
        self.assertEqual(apps["coverage"], {"desktop_seconds": 120, "browser_seconds": 60})
        self.assertEqual(domains["ranking"][0]["key"], "study.example")
        self.assertEqual(sum(p["active_seconds"] for p in domains["timeline"]), 60)

    def test_scope_revocation_and_browser_binding(self):
        other = self.repo.create_workspace("Other synthetic workspace", now=self.now)
        with self.assertRaises(ValueError):
            self.repo.summary(other, self.device, self.now.date())
        with self.assertRaises(ValueError):
            self.repo.ingest(other, self.device, "desktop", [self.event()], now=self.now)
        with self.assertRaises(ValueError):
            self.ingest([self.event(app="browser", domain="study.example")], "browser", browser_app_id="windows:other.exe")
        self.repo.revoke_device(self.workspace, self.device, now=self.now)
        with self.assertRaisesRegex(ValueError, "revoked"):
            self.ingest([self.event()])

    def test_validation_of_utc_retention_duration_and_platform(self):
        for changed in ({"started_at": "2026-10-01T12:00:00"}, {"ended_at": "2026-10-01T12:02:00Z"},
                        {"app_id": "linux:sample"}, {"state": "idle"}, {"event_id": "invalid"},
                        {"started_at": "2025-10-01T12:00:00Z", "ended_at": "2025-10-01T12:01:00Z"},
                        {"started_at": "2026-10-01T14:00:00Z", "ended_at": "2026-10-01T14:01:00Z"}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                self.ingest([dict(self.event(), **changed)])
        self.assertEqual(self.count(), 0)

    def test_calendar_month_week_midnight_split_and_empty_state(self):
        self.ingest([self.event("2026-09-30T23:59:30Z", "2026-10-01T00:00:30Z")])
        self.assertEqual(self.summary()["active_seconds"], 30)
        week = self.summary(period="week")
        month = self.summary(period="month")
        self.assertEqual(week["active_seconds"], 60)
        self.assertEqual(week["started_at"], "2026-09-28T00:00:00.000Z")
        self.assertEqual(len(month["timeline"]), 31)
        self.assertEqual(month["active_seconds"], 30)
        empty = self.repo.summary(self.workspace, self.device, date(2026, 11, 1))
        self.assertEqual((empty["active_seconds"], empty["ranking"]), (0, []))
        self.assertTrue(all(p["active_seconds"] == 0 for p in empty["timeline"]))

    def test_dst_days_and_repeated_hour_preserve_elapsed_seconds(self):
        try:
            zone("America/New_York")
        except ValueError:
            self.skipTest("Install the storage extra for IANA time zones")
        for day, hours in ((date(2026, 3, 8), 23), (date(2026, 11, 1), 25)):
            report = self.repo.summary(self.workspace, self.device, day, timezone_name="America/New_York")
            self.assertEqual(len(report["timeline"]), hours)
        now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
        events = [self.event("2026-11-01T05:30:00Z", "2026-11-01T05:31:00Z"),
                  self.event("2026-11-01T06:30:00Z", "2026-11-01T06:31:00Z")]
        self.repo.ingest(self.workspace, self.device, "desktop", events, now=now)
        report = self.repo.summary(self.workspace, self.device, now.date(), timezone_name="America/New_York")
        self.assertEqual(report["active_seconds"], 120)
        self.assertEqual(sum(p["active_seconds"] > 0 for p in report["timeline"]), 2)

    def test_deletion_and_retention_prevent_replayed_history(self):
        event = self.event()
        self.ingest([event])
        self.assertEqual(self.repo.delete_history(self.workspace, self.device, before=self.now), 1)
        self.assertEqual(self.count("applications"), 0)
        with self.assertRaises(ValueError):
            self.ingest([event])
        self.repo.delete_history(self.workspace, self.device, before=self.now - timedelta(days=10))
        self.assertEqual(self.db.connection.execute("SELECT ingestion_not_before FROM devices").fetchone()[0], milliseconds(self.now))
        newer = self.event("2026-10-01T13:00:00Z", "2026-10-01T13:01:00Z")
        self.ingest([newer])
        self.assertEqual(self.repo.apply_retention(self.workspace, now=self.now + timedelta(days=91)), 1)

    def test_foreign_keys_target_checks_and_cascade(self):
        self.ingest([self.event()])
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.connection.execute("INSERT INTO rules VALUES (?, ?, 'domain', NULL, NULL, 'block', 0)",
                                       (str(uuid4()), self.device))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.connection.execute("INSERT INTO devices VALUES (?, ?, 'Unknown', 'windows', 0, 0, NULL)",
                                       (str(uuid4()), str(uuid4())))
        self.repo.delete_device(self.workspace, self.device)
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.count("applications"), 0)

    def test_seed_is_repeatable_and_preserves_existing_databases(self):
        with self.assertRaises(ValueError):
            seed_demo(self.db)
        with Database(Path(self.temp.name) / "seed.sqlite3") as db:
            db.migrate()
            self.assertTrue(seed_demo(db)["created"])
            self.assertFalse(seed_demo(db)["created"])
            for table, expected in (("usage_sessions", 5), ("goals", 1), ("rules", 1), ("focus_sessions", 1)):
                self.assertEqual(db.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], expected)
            self.assertEqual(db.connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(UsageRepository(db).summary(WORKSPACE_ID, DEVICE_ID, date(2026, 10, 1))["active_seconds"], 120)

    def test_concurrent_overlaps_cannot_both_commit(self):
        def writer(event):
            with Database(self.path) as db:
                try:
                    UsageRepository(db).ingest(self.workspace, self.device, "desktop", [event], now=self.now)
                    return True
                except sqlite3.IntegrityError:
                    return False
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(writer, [self.event(), self.event()]))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(self.count(), 1)

    def test_period_query_uses_index(self):
        self.ingest([self.event()])
        plan = self.db.connection.execute("EXPLAIN QUERY PLAN SELECT * FROM usage_sessions "
                                         "WHERE device_id=? AND source='desktop' AND started_at<? AND ended_at>?",
                                         (self.device, milliseconds(self.now), 0)).fetchall()
        self.assertTrue(any("usage_period" in row[3] for row in plan))

    def test_cli_init_seed_and_summary(self):
        path = Path(self.temp.name) / "cli.sqlite3"
        base = [sys.executable, "-m", "activity_monitor.storage", "--database", str(path)]
        for command in (["init"], ["seed"], ["seed"]):
            result = subprocess.run(base + command, capture_output=True, text=True, check=True)
            self.assertIsInstance(json.loads(result.stdout), dict)
        result = subprocess.run(base + ["summary", "--workspace", WORKSPACE_ID, "--device", DEVICE_ID,
                                       "--date", "2026-10-01", "--dimension", "domain"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["active_seconds"], 60)
        self.assertNotEqual(default_database_path().parent, Path.cwd())
