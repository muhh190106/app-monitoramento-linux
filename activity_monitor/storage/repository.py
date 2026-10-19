"""Trusted local storage operations; HTTP authentication belongs to the future API."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from uuid import UUID, uuid4

from .time import DAY_MS, calendar_window, milliseconds, parse_timestamp, timestamp, zone

APP_KEY = re.compile(r"(?:windows|linux):[^\s/\\]+")
HOSTNAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*")


def identifier(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError("Expected a UUID") from error


def nonempty(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected non-empty text")
    return value


def now_ms(now=None):
    return milliseconds(datetime.now(timezone.utc) if now is None else now)


class UsageRepository:
    def __init__(self, database):
        self.db = database

    def create_workspace(self, name, timezone_name="UTC", retention_days=90, *, now=None):
        zone(timezone_name)
        if type(retention_days) is not int or not 1 <= retention_days <= 36500:
            raise ValueError("Retention must be between 1 and 36500 days")
        workspace_id = str(uuid4())
        with self.db.transaction() as conn:
            conn.execute("INSERT INTO workspaces VALUES (?, ?, ?, ?, ?)",
                         (workspace_id, nonempty(name), timezone_name, retention_days, now_ms(now)))
        return workspace_id

    def create_device(self, workspace_id, name, platform, *, now=None):
        current = now_ms(now)
        if platform not in ("windows", "linux"):
            raise ValueError("Unknown device platform")
        device_id = str(uuid4())
        with self.db.transaction() as conn:
            workspace = conn.execute("SELECT * FROM workspaces WHERE id=?", (identifier(workspace_id),)).fetchone()
            if workspace is None:
                raise ValueError("Workspace not found")
            conn.execute("INSERT INTO devices VALUES (?, ?, ?, ?, ?, ?, NULL)",
                         (device_id, workspace["id"], nonempty(name), platform,
                          current - workspace["retention_days"] * DAY_MS, current))
        return device_id

    @staticmethod
    def _device(conn, workspace_id, device_id):
        device = conn.execute("SELECT d.*, w.retention_days FROM devices d JOIN workspaces w "
                              "ON w.id=d.workspace_id WHERE d.id=? AND d.workspace_id=?",
                              (identifier(device_id), identifier(workspace_id))).fetchone()
        if device is None:
            raise ValueError("Device not found in workspace")
        return device

    @staticmethod
    def _event(event, source, platform):
        required = {"event_id", "started_at", "ended_at", "state"}
        if not isinstance(event, dict) or not required <= event.keys():
            raise ValueError("Missing event fields")
        state = event["state"]
        if state not in ("active", "idle") or (source == "browser" and state != "active"):
            raise ValueError("Invalid event state")
        allowed = required | ({"app_id", "app_name"} if state == "active" else set())
        if source == "browser":
            allowed.add("domain")
        if set(event) != allowed:
            raise ValueError("Unexpected or missing event fields")
        normalized = dict(event, event_id=identifier(event["event_id"]))
        start, end = parse_timestamp(event["started_at"]), parse_timestamp(event["ended_at"])
        if not 0 < end - start <= 60000:
            raise ValueError("Event duration must be greater than zero and at most 60 seconds")
        normalized.update(started_at=timestamp(start), ended_at=timestamp(end))
        if state == "active":
            key = event["app_id"]
            if (not isinstance(key, str) or len(key) > 255 or not APP_KEY.fullmatch(key)
                    or not key.startswith(platform + ":")):
                raise ValueError("Invalid application key or platform")
            if len(nonempty(event["app_name"])) > 200:
                raise ValueError("Application name is too long")
        if source == "browser":
            domain = event["domain"]
            if not isinstance(domain, str) or len(domain) > 253 or not HOSTNAME.fullmatch(domain):
                raise ValueError("Invalid canonical domain")
        digest = sha256(json.dumps({"source": source, **normalized}, sort_keys=True,
                                   separators=(",", ":")).encode()).hexdigest()
        return normalized, start, end, digest

    @staticmethod
    def _application(conn, key, name, platform):
        row = conn.execute("SELECT id FROM applications WHERE app_key=?", (key,)).fetchone()
        if row:
            return row[0]
        app_id = str(uuid4())
        conn.execute("INSERT INTO applications VALUES (?, ?, ?, ?)", (app_id, key, name, platform))
        return app_id

    @staticmethod
    def _domain(conn, hostname):
        row = conn.execute("SELECT id FROM domains WHERE hostname=?", (hostname,)).fetchone()
        if row:
            return row[0]
        domain_id = str(uuid4())
        conn.execute("INSERT INTO domains VALUES (?, ?)", (domain_id, hostname))
        return domain_id

    def ingest(self, workspace_id, device_id, source, events, *, browser_app_id=None, now=None):
        """Write one atomic batch. Caller supplies an already authorized workspace/device.

        For browser events, browser_app_id is the trusted pairing value, not input
        copied from the request body. This method does not authenticate tokens.
        """
        if source not in ("desktop", "browser") or not isinstance(events, list) or not 1 <= len(events) <= 500:
            raise ValueError("Expected 1 to 500 events from desktop or browser")
        if source == "browser" and not browser_app_id:
            raise ValueError("A trusted browser application binding is required")
        current = now_ms(now)
        accepted, duplicates = [], []
        with self.db.transaction() as conn:
            device = self._device(conn, workspace_id, device_id)
            if device["revoked_at"] is not None:
                raise ValueError("Device is revoked")
            cutoff = max(device["ingestion_not_before"], current - device["retention_days"] * DAY_MS)
            seen = set()
            for raw in events:
                event, start, end, digest = self._event(raw, source, device["platform"])
                event_id = event["event_id"]
                if event_id in seen:
                    raise ValueError("Duplicate event ID within batch")
                seen.add(event_id)
                if start < cutoff or end > current + 300000:
                    raise ValueError("Event is outside retention or in the future")
                if source == "browser" and event["app_id"] != browser_app_id:
                    raise ValueError("Browser application does not match pairing")
                previous = conn.execute("SELECT payload_hash FROM usage_sessions WHERE device_id=? AND event_id=?",
                                        (device["id"], event_id)).fetchone()
                if previous:
                    if previous[0] != digest:
                        raise ValueError("Event ID conflicts with previous content")
                    duplicates.append(event_id)
                    continue
                app_id = self._application(conn, event["app_id"], event["app_name"], device["platform"]) if event["state"] == "active" else None
                domain_id = self._domain(conn, event["domain"]) if source == "browser" else None
                conn.execute("INSERT INTO usage_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (str(uuid4()), device["id"], event_id, source, event["state"],
                              app_id, domain_id, start, end, current, digest))
                accepted.append(event_id)
        return {"accepted_event_ids": accepted, "duplicate_event_ids": duplicates}

    @staticmethod
    def _aggregate(conn, device_id, dimension, start, end):
        if dimension == "application":
            sql = """SELECT u.state, a.app_key AS key, a.display_name AS label,
                SUM(MIN(u.ended_at, :end) - MAX(u.started_at, :start)) / 1000.0 AS seconds
                FROM usage_sessions u LEFT JOIN applications a ON a.id=u.application_id
                WHERE u.device_id=:device AND u.source='desktop'
                  AND u.started_at < :end AND u.ended_at > :start
                GROUP BY u.state, a.app_key, a.display_name"""
        else:
            sql = """SELECT 'active' AS state, n.hostname AS key, n.hostname AS label,
                SUM(MIN(b.ended_at, d.ended_at, :end) - MAX(b.started_at, d.started_at, :start)) / 1000.0 AS seconds
                FROM usage_sessions b JOIN usage_sessions d ON d.device_id=b.device_id
                  AND d.application_id=b.application_id AND d.source='desktop' AND d.state='active'
                  AND d.started_at < b.ended_at AND d.ended_at > b.started_at
                JOIN domains n ON n.id=b.domain_id
                WHERE b.device_id=:device AND b.source='browser'
                  AND b.started_at < :end AND b.ended_at > :start
                  AND d.started_at < :end AND d.ended_at > :start
                GROUP BY n.hostname"""
        return [dict(row) for row in conn.execute(sql, {"device": device_id, "start": start, "end": end})]

    def summary(self, workspace_id, device_id, reference, period="day", timezone_name="UTC", dimension="application"):
        if dimension not in ("application", "domain"):
            raise ValueError("Unknown report dimension")
        start, end, buckets = calendar_window(reference, period, timezone_name)
        with self.db.transaction(write=False) as conn:
            device = self._device(conn, workspace_id, device_id)
            device_id = device["id"]
            apps = self._aggregate(conn, device_id, "application", start, end)
            domains = self._aggregate(conn, device_id, "domain", start, end)
            rows = apps if dimension == "application" else domains
            active = sum(r["seconds"] for r in rows if r["state"] == "active")
            idle = sum(r["seconds"] for r in rows if r["state"] == "idle")
            ranking = [{"key": r["key"], "label": r["label"], "seconds": r["seconds"],
                        "share": r["seconds"] / active} for r in rows if r["state"] == "active" and active]
            ranking.sort(key=lambda r: (-r["seconds"], r["key"]))
            timeline = []
            for left, right in buckets:
                grouped = self._aggregate(conn, device_id, dimension, left, right) if right > left else []
                timeline.append({"started_at": timestamp(left), "ended_at": timestamp(right),
                                 "active_seconds": sum(r["seconds"] for r in grouped if r["state"] == "active"),
                                 "idle_seconds": sum(r["seconds"] for r in grouped if r["state"] == "idle")})
        return {"device_id": device_id, "date": reference.isoformat(), "period": period,
                "timezone": timezone_name, "dimension": dimension, "started_at": timestamp(start),
                "ended_at": timestamp(end), "active_seconds": active, "idle_seconds": idle,
                "coverage": {"desktop_seconds": sum(r["seconds"] for r in apps),
                             "browser_seconds": sum(r["seconds"] for r in domains)},
                "ranking": ranking, "timeline": timeline}

    @staticmethod
    def _clean_catalog(conn):
        conn.execute("DELETE FROM domains WHERE id NOT IN (SELECT domain_id FROM usage_sessions WHERE domain_id IS NOT NULL) "
                     "AND id NOT IN (SELECT domain_id FROM goals WHERE domain_id IS NOT NULL) "
                     "AND id NOT IN (SELECT domain_id FROM rules WHERE domain_id IS NOT NULL) "
                     "AND hostname NOT IN (SELECT target_key FROM focus_session_rules WHERE target_type='domain')")
        conn.execute("DELETE FROM applications WHERE id NOT IN (SELECT application_id FROM usage_sessions WHERE application_id IS NOT NULL) "
                     "AND id NOT IN (SELECT application_id FROM goals WHERE application_id IS NOT NULL) "
                     "AND id NOT IN (SELECT application_id FROM rules WHERE application_id IS NOT NULL) "
                     "AND id NOT IN (SELECT browser_application_id FROM access_tokens WHERE browser_application_id IS NOT NULL) "
                     "AND app_key NOT IN (SELECT target_key FROM focus_session_rules WHERE target_type='application')")

    def delete_history(self, workspace_id, device_id, *, before):
        cutoff = milliseconds(before)
        with self.db.transaction() as conn:
            device = self._device(conn, workspace_id, device_id)
            cutoff = max(cutoff, device["ingestion_not_before"])
            count = conn.execute("DELETE FROM usage_sessions WHERE device_id=? AND started_at<?", (device["id"], cutoff)).rowcount
            conn.execute("UPDATE devices SET ingestion_not_before=? WHERE id=?", (cutoff, device["id"]))
            self._clean_catalog(conn)
        return count

    def apply_retention(self, workspace_id, *, now=None):
        current = now_ms(now)
        with self.db.transaction() as conn:
            workspace_id = identifier(workspace_id)
            if conn.execute("SELECT 1 FROM workspaces WHERE id=?", (workspace_id,)).fetchone() is None:
                raise ValueError("Workspace not found")
            count = 0
            for device in conn.execute("SELECT d.*, w.retention_days FROM devices d JOIN workspaces w ON w.id=d.workspace_id WHERE w.id=?", (workspace_id,)).fetchall():
                cutoff = max(device["ingestion_not_before"], current - device["retention_days"] * DAY_MS)
                count += conn.execute("DELETE FROM usage_sessions WHERE device_id=? AND started_at<?", (device["id"], cutoff)).rowcount
                conn.execute("UPDATE devices SET ingestion_not_before=? WHERE id=?", (cutoff, device["id"]))
            conn.execute("DELETE FROM idempotency_requests WHERE workspace_id=? AND expires_at<=?", (workspace_id, current))
            self._clean_catalog(conn)
        return count

    def revoke_device(self, workspace_id, device_id, *, now=None):
        with self.db.transaction() as conn:
            device = self._device(conn, workspace_id, device_id)
            current = now_ms(now)
            conn.execute("UPDATE devices SET revoked_at=COALESCE(revoked_at, ?) WHERE id=?", (current, device["id"]))
            conn.execute("UPDATE access_tokens SET revoked_at=COALESCE(revoked_at, ?) WHERE device_id=?", (current, device["id"]))

    def delete_device(self, workspace_id, device_id):
        with self.db.transaction() as conn:
            device = self._device(conn, workspace_id, device_id)
            conn.execute("DELETE FROM devices WHERE id=?", (device["id"],))
            self._clean_catalog(conn)
