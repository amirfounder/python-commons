from datetime import timezone, datetime
from typing import Optional


def now(tz: Optional[timezone] = None):
    if not tz:
        tz = timezone.utc
    return datetime.now(tz)


def format_iso(dt: datetime):
    return dt.isoformat()


def parse_iso(s: str):
    return datetime.fromisoformat(s)
