"""Command-line interface for the synthetic activity demo."""

import argparse
import json

from . import __version__
from .summary import summarize


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="activity-monitor",
        description="Understand your time. Own your data.",
        epilog="Early development: desktop activity collection is not available yet.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--demo", action="store_true", help="Summarize synthetic events without collecting activity"
    )
    args = parser.parse_args(argv)
    if not args.demo:
        parser.print_help()
        return
    events = [
        {"app": "Editor", "seconds": 120, "afk": False},
        {"app": "Browser", "seconds": 60, "afk": False},
        {"app": "Editor", "seconds": 30, "afk": True},
    ]
    print(json.dumps({"demo": True, "active_seconds": summarize(events)}, indent=2))
