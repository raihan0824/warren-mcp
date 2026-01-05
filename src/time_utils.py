"""Time utilities for Warren Finance MCP Server.

Handles time range calculations in Asia/Jakarta timezone.
"""

from datetime import datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

# Asia/Jakarta timezone (UTC+7)
JAKARTA_TZ = ZoneInfo("Asia/Jakarta")

TimeRange = Literal["today", "yesterday", "this_week", "last_week", "this_month"]


def get_jakarta_now() -> datetime:
    """Get current datetime in Asia/Jakarta timezone."""
    return datetime.now(JAKARTA_TZ)


def get_time_range(range_name: TimeRange) -> tuple[datetime, datetime]:
    """
    Get start and end timestamps for a given time range in Asia/Jakarta timezone.

    Args:
        range_name: One of "today", "yesterday", "this_week", "last_week", "this_month"

    Returns:
        Tuple of (start_ts, end_ts) as timezone-aware datetime objects

    Raises:
        ValueError: If range_name is not a valid option
    """
    now = get_jakarta_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if range_name == "today":
        start_ts = today_start
        end_ts = now

    elif range_name == "yesterday":
        start_ts = today_start - timedelta(days=1)
        end_ts = today_start - timedelta(microseconds=1)

    elif range_name == "this_week":
        # Week starts on Monday (weekday() returns 0 for Monday)
        days_since_monday = now.weekday()
        start_ts = today_start - timedelta(days=days_since_monday)
        end_ts = now

    elif range_name == "last_week":
        days_since_monday = now.weekday()
        this_week_start = today_start - timedelta(days=days_since_monday)
        start_ts = this_week_start - timedelta(days=7)
        end_ts = this_week_start - timedelta(microseconds=1)

    elif range_name == "this_month":
        start_ts = today_start.replace(day=1)
        end_ts = now

    else:
        raise ValueError(f"Invalid time range: {range_name}")

    return start_ts, end_ts


def format_datetime_jakarta(dt: datetime) -> str:
    """Format a datetime object for display in Asia/Jakarta timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=JAKARTA_TZ)
    return dt.astimezone(JAKARTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
