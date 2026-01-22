from __future__ import annotations

import re
from datetime import datetime

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
PIN_RE = re.compile(r"^\d{4,6}$")


def validate_date(date_s: str) -> str:
    if not DATE_RE.match(date_s):
        raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
    datetime.strptime(date_s, "%Y-%m-%d")  # validate real date
    return date_s


def validate_time(time_s: str) -> str:
    if not TIME_RE.match(time_s):
        raise ValueError("Invalid time format. Expected HH:MM.")
    datetime.strptime(time_s, "%H:%M")
    return time_s


def validate_duration_minutes(minutes: int) -> int:
    if minutes is None or minutes <= 0:
        raise ValueError("Duration must be a positive integer (minutes).")
    return minutes


def validate_pin(pin: str) -> str:
    if not PIN_RE.match(pin or ""):
        raise ValueError("Invalid PIN. PIN must be 4–6 digits.")
    return pin


def validate_date_range(date_from: str | None, date_to: str | None) -> tuple[str | None, str | None]:
    """
    Validate optional date range:
    - if provided, must be YYYY-MM-DD
    - if both provided, from <= to
    """
    if date_from:
        validate_date(date_from)
    if date_to:
        validate_date(date_to)
    if date_from and date_to:
        d1 = datetime.strptime(date_from, "%Y-%m-%d").date()
        d2 = datetime.strptime(date_to, "%Y-%m-%d").date()
        if d1 > d2:
            raise ValueError("Invalid date range: date_from must be <= date_to.")
    return date_from, date_to


def require_session_open(session_status: str) -> None:
    """Rule helper: certain actions require session OPEN."""
    if session_status != "OPEN":
        raise ValueError("Session is not OPEN.")
