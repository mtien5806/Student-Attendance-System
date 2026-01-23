from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import secrets

from src.models.enums import SessionStatus
from src.utils.validators import validate_date, validate_time, validate_duration_minutes, validate_pin
from src.repositories.session_repo import SessionRepo
from src.repositories.class_repo import ClassRepo


@dataclass
class CreateSessionInput:
    class_id: int
    session_date: str   # YYYY-MM-DD
    start_time: str     # HH:MM
    duration_min: int
    pin_enabled: bool
    pin_code: Optional[str] = None
    lecturer_id: Optional[int] = None  # optional check ownership


class SessionService:
    """UC06 Create Attendance Session; UC07 Close Session."""

    def __init__(self) -> None:
        self.session_repo = SessionRepo()
        self.class_repo = ClassRepo()

    def create_session(self, data: CreateSessionInput) -> int:
        validate_date(data.session_date)
        validate_time(data.start_time)
        validate_duration_minutes(data.duration_min)

        cls = self.class_repo.get_by_id(data.class_id)
        if not cls:
            raise ValueError("Class not found.")
        if data.lecturer_id is not None and cls.lecturer_id != data.lecturer_id:
            raise ValueError("You are not the lecturer of this class.")

        pin_code: Optional[str] = None
        pin_enabled_int = 1 if data.pin_enabled else 0
        if data.pin_enabled:
            if data.pin_code and data.pin_code.strip():
                pin_code = validate_pin(data.pin_code.strip())
            else:
                pin_code = f"{secrets.randbelow(1_000_000):06d}"

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return self.session_repo.create(
            class_id=data.class_id,
            session_date=data.session_date,
            start_time=data.start_time,
            duration_min=data.duration_min,
            pin_enabled=pin_enabled_int,
            pin_code=pin_code,
            status=SessionStatus.OPEN.value,
            created_at=created_at,
        )

    def close_session(self, session_id: int) -> None:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found.")
        if session.status == SessionStatus.CLOSED.value:
            return
        self.session_repo.update(session_id, status=SessionStatus.CLOSED.value)
