"""
TruthLens AI — Date Utilities
Robust date parsing for RSS feeds (wildly inconsistent date formats).
"""
from datetime import datetime, timezone
from typing import Optional
import dateparser


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def parse_date(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parse a date string in virtually any format to a timezone-aware UTC datetime.
    Handles RSS, ISO 8601, human-readable formats, and more.

    Examples:
        "Thu, 31 Jul 2026 15:30:00 +0000" → datetime(2026, 7, 31, 15, 30, tzinfo=UTC)
        "2026-07-31T15:30:00Z"            → datetime(2026, 7, 31, 15, 30, tzinfo=UTC)
        "July 31, 2026"                   → datetime(2026, 7, 31, 0, 0, tzinfo=UTC)

    Returns None if parsing fails.
    """
    if not date_string:
        return None

    try:
        parsed = dateparser.parse(
            date_string,
            settings={
                "RETURN_AS_TIMEZONE_AWARE": True,
                "TO_TIMEZONE": "UTC",
                "PREFER_DAY_OF_MONTH": "first",
            },
        )
        return parsed
    except Exception:
        return None


def format_relative(dt: Optional[datetime]) -> str:
    """
    Format a datetime as a human-readable relative string.
    Examples: "2 hours ago", "3 days ago", "just now"
    """
    if dt is None:
        return "unknown"

    now = utc_now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return dt.strftime("%b %d, %Y")
