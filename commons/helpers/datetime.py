from datetime import timezone, datetime


def now(tz=timezone.utc):
    return datetime.now(tz)
