from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import secrets

from src.utils import validators


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

    def create_session(self, data: CreateSessionInput) -> int:
        # Validate input formats
        validators.validate_date(data.session_date)
        validators.validate_time(data.start_time)
        validators.validate_duration_minutes(data.duration_min)

        # PIN policy
        if data.pin_enabled:
            if data.pin_code:
                validators.validate_pin(data.pin_code)
            else:
                # auto-generate if not provided
                data.pin_code = f"{secrets.randbelow(1_000_000):06d}"

        # TODO: insert to DB via SessionRepo and return new session_id
        raise NotImplementedError("create_session not implemented yet.")

    def close_session(self, session_id: int) -> None:
        # TODO: update session status OPEN -> CLOSED
        raise NotImplementedError("close_session not implemented yet.")
