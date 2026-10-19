"""Explicit, deterministic synthetic fixtures for a separate development database."""

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from .repository import UsageRepository
from .time import DAY_MS, milliseconds

WORKSPACE_ID = "00000000-0000-4000-8000-000000000001"
DEVICE_ID = "00000000-0000-4000-8000-000000000002"
REFERENCE = datetime(2026, 10, 1, 13, tzinfo=timezone.utc)


def sample_id(name):
    return str(uuid5(NAMESPACE_URL, "https://stime.example/fixtures/" + name))


def seed_demo(database):
    """Seed an empty database once; never reset an existing user's database."""
    now = milliseconds(REFERENCE)
    with database.transaction() as conn:
        spaces = conn.execute("SELECT id FROM workspaces").fetchall()
        if spaces:
            if len(spaces) == 1 and spaces[0][0] == WORKSPACE_ID and conn.execute(
                "SELECT 1 FROM devices WHERE id=? AND workspace_id=?", (DEVICE_ID, WORKSPACE_ID)
            ).fetchone():
                return {"created": False, "workspace_id": WORKSPACE_ID, "device_id": DEVICE_ID}
            raise ValueError("Synthetic seed requires an empty or previously seeded demo database")
        if conn.execute("SELECT 1 FROM applications UNION ALL SELECT 1 FROM domains LIMIT 1").fetchone():
            raise ValueError("Synthetic seed requires an empty database catalog")
        conn.execute("INSERT INTO workspaces VALUES (?, ?, 'UTC', 90, ?)", (WORKSPACE_ID, "Synthetic workspace", now))
        conn.execute("INSERT INTO devices VALUES (?, ?, ?, 'windows', ?, ?, NULL)",
                     (DEVICE_ID, WORKSPACE_ID, "Synthetic device", now - 90 * DAY_MS, now))
        for app, label in (("editor", "Editor"), ("browser", "Browser")):
            conn.execute("INSERT INTO applications VALUES (?, ?, ?, 'windows')",
                         (sample_id("app-" + app), f"windows:sample-{app}.exe", "Sample " + label))
        conn.execute("INSERT INTO domains VALUES (?, 'study.example')", (sample_id("domain"),))
        schedule = [("desktop", "active", 0, "sample-editor.exe", "Sample Editor", None),
                    ("desktop", "active", 1, "sample-browser.exe", "Sample Browser", None),
                    ("desktop", "idle", 2, None, None, None),
                    ("browser", "active", 0, "sample-browser.exe", "Sample Browser", "study.example"),
                    ("browser", "active", 1, "sample-browser.exe", "Sample Browser", "study.example")]
        for source, state, minute, key, label, domain in schedule:
            event = {"event_id": sample_id(f"{source}-{minute}"), "state": state,
                     "started_at": f"2026-10-01T12:0{minute}:00Z", "ended_at": f"2026-10-01T12:0{minute + 1}:00Z"}
            if key:
                event.update(app_id="windows:" + key, app_name=label)
            if domain:
                event["domain"] = domain
            event, start, end, digest = UsageRepository._event(event, source, "windows")
            app_id = UsageRepository._application(conn, event["app_id"], label, "windows") if key else None
            domain_id = UsageRepository._domain(conn, domain) if domain else None
            conn.execute("INSERT INTO usage_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (sample_id("row-" + event["event_id"]), DEVICE_ID, event["event_id"], source,
                          state, app_id, domain_id, start, end, now, digest))
        domain_id = conn.execute("SELECT id FROM domains WHERE hostname='study.example'").fetchone()[0]
        conn.execute("INSERT INTO goals VALUES (?, ?, 'all', NULL, NULL, 'day', 'UTC', 3600, ?)",
                     (sample_id("goal"), DEVICE_ID, now))
        conn.execute("INSERT INTO rules VALUES (?, ?, 'domain', NULL, ?, 'block', ?)",
                     (sample_id("rule"), DEVICE_ID, domain_id, now))
        conn.execute("INSERT INTO focus_sessions VALUES (?, ?, 'completed', ?, ?, ?, ?)",
                     (sample_id("focus"), DEVICE_ID, now - 1500000, now, now, now - 1500000))
        conn.execute("INSERT INTO focus_session_rules VALUES (?, ?, 'domain', 'study.example', 'block')",
                     (sample_id("focus-rule"), sample_id("focus")))
    return {"created": True, "workspace_id": WORKSPACE_ID, "device_id": DEVICE_ID}
