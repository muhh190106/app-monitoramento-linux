"""Explicit SQLite connections and transactional, checksum-verified migrations."""

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from importlib.resources import files
import os
from pathlib import Path
import sqlite3
import sys


def default_database_path():
    """Return an OS user-data path without creating directories or files."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    else:
        configured = Path(os.environ.get("XDG_DATA_HOME", ""))
        base = configured if configured.is_absolute() else Path.home() / ".local/share"
    return base / "STimeNOW" / "activity.sqlite3"


class Database:
    def __init__(self, path=None):
        if sqlite3.sqlite_version_info < (3, 37):
            raise RuntimeError("SQLite 3.37 or later is required")
        self.path = Path(path) if path is not None else default_database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, isolation_level=None, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @contextmanager
    def transaction(self, *, write=True):
        if self.connection.in_transaction:
            raise RuntimeError("Nested transactions are not supported")
        self.connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
        try:
            yield self.connection
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise

    def migrate(self, *, target=None):
        """Apply forward migrations atomically. target supports upgrade testing only."""
        migrations = sorted(files(__package__).joinpath("migrations").iterdir(), key=lambda p: p.name)
        migrations = [p for p in migrations if p.name.endswith(".sql")]
        latest = len(migrations)
        target = latest if target is None else target
        if type(target) is not int or not 1 <= target <= latest:
            raise ValueError("Unknown migration target")
        with self.transaction() as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if tables and "schema_migrations" not in tables:
                raise ValueError("Refusing to migrate an unrecognized database")
            conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, "
                         "name TEXT NOT NULL, checksum TEXT NOT NULL, applied_at TEXT NOT NULL) STRICT")
            applied = {r["version"]: r for r in conn.execute("SELECT * FROM schema_migrations")}
            if sorted(applied) != list(range(1, len(applied) + 1)) or len(applied) > target:
                raise ValueError("Unknown, incomplete or newer migration history")
            for version, resource in enumerate(migrations, 1):
                source = resource.read_text(encoding="utf-8")
                checksum = sha256(source.encode()).hexdigest()
                if version in applied:
                    if applied[version]["checksum"] != checksum or applied[version]["name"] != resource.name:
                        raise ValueError("Applied migration has changed")
                    continue
                if version > target:
                    break
                statement = ""
                for line in source.splitlines(keepends=True):
                    statement += line
                    if sqlite3.complete_statement(statement):
                        conn.execute(statement)
                        statement = ""
                if statement.strip():
                    raise ValueError("Incomplete SQL migration")
                conn.execute("INSERT INTO schema_migrations VALUES (?, ?, ?, ?)",
                             (version, resource.name, checksum, datetime.now(timezone.utc).isoformat()))
        return target
