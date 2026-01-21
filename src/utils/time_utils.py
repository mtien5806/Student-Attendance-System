from __future__ import annotations

from datetime import datetime, timedelta


def now() -> datetime:
    return datetime.now()


def minutes_from_now(minutes: int) -> datetime:
    return now() + timedelta(minutes=minutes)
