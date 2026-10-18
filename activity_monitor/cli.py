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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--demo", action="store_true", help="Summarize synthetic events without collecting activity"
    )
    mode.add_argument("--desktop", action="store_true", help="Open the desktop dashboard with sample activity")
    parser.add_argument("--language", choices=("en", "pt-BR"), default="en", help="Desktop interface language")
    args = parser.parse_args(argv)
    if args.desktop:
        try:
            from .desktop import launch
        except ImportError as error:
            parser.error(
                "Desktop support requires tkinter, pandas, and matplotlib. "
                "Install with: python -m pip install -e '.[desktop]'. "
                "On Linux, install your distribution's Tk package too. "
                f"Missing dependency: {error.name}"
            )
        import tkinter as tk
        try:
            launch(args.language)
        except tk.TclError:
            parser.exit(2, "Unable to open the desktop interface. Check that a graphical display and Tk are available.\n")
        return
    if not args.demo:
        parser.print_help()
        return
    events = [
        {"app": "Editor", "seconds": 120, "afk": False},
        {"app": "Browser", "seconds": 60, "afk": False},
        {"app": "Editor", "seconds": 30, "afk": True},
    ]
    print(json.dumps({"demo": True, "active_seconds": summarize(events)}, indent=2))
