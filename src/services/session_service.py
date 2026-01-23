from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import secrets

from src.utils import validators
from src.repositories.session_repo import SessionRepo


@dataclass
class CreateSessionInput:
    class_id: int
    session_date: str   # YYYY-MM-DD
    start_time: str     # HH:MM
    duration_min: int
    pin_enabled: bool
    pin_code: Optional[str] = None


class SessionService:
    """UC06 Create Attendance Session; UC07 Close session (skeleton)."""

    def __init__(self):
        self.session_repo = SessionRepo()

    def create_session(self, data: CreateSessionInput) -> int:
        # Validate input formats
        validators.validate_date(data.session_date)
        validators.validate_time(data.start_time)
        validators.validate_duration_minutes(data.duration_min)
        validators.validate_date_range()

        # PIN policy
        if data.pin_enabled:
            if data.pin_code:
                validators.validate_pin(data.pin_code)
            else:
                # auto-generate if not provided
                data.pin_code = f"{secrets.randbelow(1_000_000):06d}"

        # ===== TODO IMPLEMENTATION =====
        session_id = self.session_repo.create({
            "class_id": data.class_id,
            "session_date": data.session_date,
            "start_time": data.start_time,
            "duration_min": data.duration_min,
            "pin_enabled": data.pin_enabled,
            "pin_code": data.pin_code,
            "status": "OPEN"
        })

        return session_id

    def close_session(self, session_id: int) -> None:
        # ===== TODO IMPLEMENTATION =====
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status == "CLOSED":
            return  # already closed, no action

        self.session_repo.update_status(session_id, "CLOSED")
