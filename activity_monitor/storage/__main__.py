"""Local database administration. No HTTP service or monitoring is started."""

import argparse
from datetime import date, timedelta
import json
import sqlite3

from .database import Database
from .repository import UsageRepository
from .seed import seed_demo
from .time import EPOCH, parse_timestamp


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage the local STime NOW database")
    parser.add_argument("--database", help="Database path; defaults to the OS user-data directory")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Apply forward migrations without replacing existing data")
    commands.add_parser("seed", help="Explicitly add synthetic fixtures to a separate database")
    query = commands.add_parser("summary", help="Query persisted usage")
    query.add_argument("--workspace", required=True)
    query.add_argument("--device", required=True)
    query.add_argument("--date", required=True, type=date.fromisoformat)
    query.add_argument("--period", choices=("day", "week", "month"), default="day")
    query.add_argument("--timezone", default="UTC")
    query.add_argument("--dimension", choices=("application", "domain"), default="application")
    retention = commands.add_parser("retain", help="Apply the workspace retention policy")
    retention.add_argument("--workspace", required=True)
    deletion = commands.add_parser("delete-history", help="Delete intervals starting before a UTC cutoff")
    deletion.add_argument("--workspace", required=True)
    deletion.add_argument("--device", required=True)
    deletion.add_argument("--before", required=True)
    deletion.add_argument("--confirm", action="store_true", help="Confirm the requested local deletion")
    args = parser.parse_args(argv)
    if args.command == "seed" and args.database is None:
        parser.error("Seed requires an explicit --database path for a separate synthetic database")
    if args.command == "delete-history" and not args.confirm:
        parser.error("History deletion requires --confirm")
    try:
        with Database(args.database) as db:
            version = db.migrate()
            repository = UsageRepository(db)
            if args.command == "init":
                result = {"schema_version": version, "database": str(db.path)}
            elif args.command == "seed":
                result = seed_demo(db)
            elif args.command == "summary":
                result = repository.summary(args.workspace, args.device, args.date, args.period, args.timezone, args.dimension)
            elif args.command == "retain":
                result = {"deleted_events": repository.apply_retention(args.workspace)}
            else:
                before = EPOCH + timedelta(milliseconds=parse_timestamp(args.before))
                result = {"deleted_events": repository.delete_history(args.workspace, args.device, before=before)}
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, sqlite3.Error, RuntimeError) as error:
        parser.exit(2, f"Database operation failed: {error}\n")


if __name__ == "__main__":
    main()
