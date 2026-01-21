from __future__ import annotations

import re
from datetime import datetime

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
PIN_RE = re.compile(r"^\d{4,6}$")


def validate_date(date_s: str) -> str:
    if not DATE_RE.match(date_s):
        raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
    datetime.strptime(date_s, "%Y-%m-%d")
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
