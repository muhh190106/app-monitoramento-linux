"""Pure reporting boundary for a single device's normalized local intervals.

This first desktop increment uses local wall-clock timestamps and synthetic data.
Time zones and multiple devices belong to the storage/collector increment.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class UsageInterval:
    app: str
    start: datetime
    end: datetime
    afk: bool = False

    def __post_init__(self):
        if not isinstance(self.app, str) or not self.app.strip():
            raise ValueError("Application name must not be empty")
        if not isinstance(self.afk, bool):
            raise ValueError("Idle state must be a boolean")
        if not isinstance(self.start, datetime) or not isinstance(self.end, datetime):
            raise ValueError("Interval boundaries must be datetimes")
        if self.start.tzinfo is not None or self.end.tzinfo is not None:
            raise ValueError("This demo accepts local wall-clock timestamps only")
        if self.end <= self.start:
            raise ValueError("Interval end must be after its start")


@dataclass(frozen=True)
class ApplicationUsage:
    app: str
    seconds: float
    share: float


@dataclass(frozen=True)
class TimelinePoint:
    timestamp: datetime
    active_seconds: float
    idle_seconds: float


@dataclass(frozen=True)
class UsageReport:
    start: date
    end: date
    active_seconds: float
    idle_seconds: float
    applications: tuple[ApplicationUsage, ...]
    timeline: tuple[TimelinePoint, ...]


def build_report(
    intervals: Iterable[UsageInterval], reference: date, days: int = 1,
    application: str | None = None,
) -> UsageReport:
    """Clip intervals to a period and split them at chart bucket boundaries.

    Overlap is rejected so reports cannot silently double-count activity. Idle
    intervals contribute to idle totals but never to application ranking.
    """
    if isinstance(days, bool) or not isinstance(days, int) or days not in (1, 7, 30):
        raise ValueError("Period must be 1, 7, or 30 days")
    try:
        start = datetime.combine(reference - timedelta(days=days - 1), time.min)
        end = datetime.combine(reference + timedelta(days=1), time.min)
    except OverflowError as error:
        raise ValueError("Date outside supported report range") from error
    ordered = sorted(intervals, key=lambda event: event.start)
    for previous, current in zip(ordered, ordered[1:]):
        if current.start < previous.end:
            raise ValueError("Activity intervals must not overlap")

    rows = []
    hourly = days == 1
    for event in ordered:
        if application is not None and event.app != application:
            continue
        cursor, stop = max(event.start, start), min(event.end, end)
        while cursor < stop:
            bucket = cursor.replace(minute=0, second=0, microsecond=0) if hourly else datetime.combine(cursor.date(), time.min)
            next_bucket = bucket + (timedelta(hours=1) if hourly else timedelta(days=1))
            segment_end = min(stop, next_bucket)
            rows.append((bucket, event.app, (segment_end - cursor).total_seconds(), event.afk))
            cursor = segment_end

    buckets = pd.date_range(start, end, freq="h" if hourly else "D", inclusive="left")
    if not rows:
        return UsageReport(start.date(), reference, 0, 0, (), tuple(
            TimelinePoint(stamp.to_pydatetime(), 0, 0) for stamp in buckets
        ))
    frame = pd.DataFrame(rows, columns=["bucket", "app", "seconds", "afk"])
    active = frame.loc[~frame["afk"]]
    idle = frame.loc[frame["afk"]]
    active_seconds = float(active["seconds"].sum())
    idle_seconds = float(idle["seconds"].sum())
    ranking = active.groupby("app")["seconds"].sum().sort_values(ascending=False, kind="stable")
    applications = tuple(ApplicationUsage(name, float(seconds), float(seconds / active_seconds)) for name, seconds in ranking.items())
    active_buckets = active.groupby("bucket")["seconds"].sum().reindex(buckets, fill_value=0)
    idle_buckets = idle.groupby("bucket")["seconds"].sum().reindex(buckets, fill_value=0)
    timeline = tuple(TimelinePoint(stamp.to_pydatetime(), float(active_buckets.loc[stamp]), float(idle_buckets.loc[stamp])) for stamp in buckets)
    return UsageReport(start.date(), reference, active_seconds, idle_seconds, applications, timeline)


def demo_intervals(anchor: date) -> tuple[UsageInterval, ...]:
    """Generate 30 days of deterministic, non-overlapping fictional usage."""
    events = []
    schedule = (("Editor", 9, 0, 75, False), ("Browser", 10, 20, 40, False),
                ("Browser", 11, 0, 20, True), ("Terminal", 11, 20, 35, False),
                ("Meet", 13, 0, 45, False), ("Editor", 14, 0, 90, False),
                ("Mail", 15, 40, 25, False), ("Browser", 16, 10, 35, False))
    for offset in range(30):
        day = anchor - timedelta(days=offset)
        if day.weekday() >= 5 and offset != 0:
            continue
        for app, hour, minute, duration, idle in schedule:
            start = datetime.combine(day, time(hour, minute))
            # Shorter historical days provide a visibly useful timeline.
            length = duration if offset == 0 else max(5, duration - (offset % 4) * 5)
            events.append(UsageInterval(app, start, start + timedelta(minutes=length), idle))
    return tuple(events)


def format_duration(seconds: float) -> str:
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, remainder = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m" if minutes else f"{remainder}s"
