"""Aggregate validated activity intervals without platform dependencies."""

import math
from collections.abc import Iterable
from typing import TypedDict


class ActivityEvent(TypedDict):
    """A normalized interval; callers must resolve overlapping intervals first."""

    app: str
    seconds: int | float
    afk: bool


def summarize(events: Iterable[ActivityEvent]) -> dict[str, int | float]:
    """Sum active seconds by application, excluding intervals marked as idle.

    Events must be normalized and non-overlapping. Missing fields raise KeyError;
    invalid field values raise ValueError, including values in idle events.
    """
    totals: dict[str, int | float] = {}
    for event in events:
        app, seconds, afk = event["app"], event["seconds"], event["afk"]
        if not isinstance(app, str) or not app.strip():
            raise ValueError("app must be a non-empty string")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise ValueError("seconds must be a number")
        if seconds < 0 or (isinstance(seconds, float) and not math.isfinite(seconds)):
            raise ValueError("seconds must be finite and non-negative")
        if not isinstance(afk, bool):
            raise ValueError("afk must be a boolean")
        if not afk:
            total = totals.get(app, 0) + seconds
            if isinstance(total, float) and not math.isfinite(total):
                raise ValueError("total active seconds must be finite")
            totals[app] = total
    return totals
