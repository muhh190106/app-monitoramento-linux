"""UTC millisecond values and calendar boundaries for persisted observations."""

from datetime import date, datetime, time, timedelta, timezone
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
DAY_MS = 86400000


def zone(name):
    if name == "UTC":
        return UTC
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as error:
        raise ValueError("Unknown time zone; install the storage extra for IANA data") from error


def milliseconds(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An aware datetime is required")
    delta = value.astimezone(UTC) - EPOCH
    return (delta.days * 86400 + delta.seconds) * 1000 + delta.microseconds // 1000


def parse_timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z", value
    ):
        raise ValueError("Expected a UTC timestamp ending in Z")
    return milliseconds(datetime.fromisoformat(value.replace("Z", "+00:00")))


def timestamp(value):
    return (EPOCH + timedelta(milliseconds=value)).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def calendar_window(reference, period, timezone_name):
    if type(reference) is not date or not 2 <= reference.year <= 9998:
        raise ValueError("Expected a calendar date between years 2 and 9998")
    tz = zone(timezone_name)
    if period == "day":
        first, stop = reference, reference + timedelta(days=1)
    elif period == "week":
        first = reference - timedelta(days=reference.weekday())
        stop = first + timedelta(days=7)
    elif period == "month":
        first = reference.replace(day=1)
        stop = date(first.year + (first.month == 12), first.month % 12 + 1, 1)
    else:
        raise ValueError("Period must be day, week or month")
    boundary = lambda day: milliseconds(datetime.combine(day, time.min, tz))
    start, end = boundary(first), boundary(stop)
    buckets = []
    if period == "day":
        cursor = start
        while cursor < end:
            next_boundary = min(cursor + 3600000, end)
            buckets.append((cursor, next_boundary))
            cursor = next_boundary
    else:
        cursor = first
        while cursor < stop:
            next_date = cursor + timedelta(days=1)
            buckets.append((boundary(cursor), boundary(next_date)))
            cursor = next_date
    return start, end, buckets
