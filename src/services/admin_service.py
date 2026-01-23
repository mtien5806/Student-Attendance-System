from __future__ import annotations

from typing import Optional, Any

from src.models.enums import AttendanceStatus
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.session_repo import SessionRepo
from src.repositories.enrollment_repo import EnrollmentRepo


class AdminService:
    """UC05 Search Attendance; UC10 Manage Attendance."""

    def __init__(self) -> None:
        self._attendance_repo = AttendanceRepo()
        self._session_repo = SessionRepo()
        self._enrollment_repo = EnrollmentRepo()

    def search_attendance(
        self,
        *,
        student_id: Optional[int] = None,
        session_id: Optional[int] = None,
        class_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        records = self._attendance_repo.list_by_filter(
            student_id=student_id,
            session_id=session_id,
            class_id=class_id,
            date_from=date_from,
            date_to=date_to,
        )
        return [vars(r) for r in records]

    def add_record(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> int:
        self._validate_record(session_id, student_id, status)
        return self._attendance_repo.create(session_id=session_id, student_id=student_id, status=status, note=note)

    def edit_record(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> None:
        self._validate_record(session_id, student_id, status)
        rec = self._attendance_repo.get_by_session_student(session_id, student_id)
        if not rec:
            raise ValueError("Record not found.")
        self._attendance_repo.update(session_id=session_id, student_id=student_id, status=status, note=note)

    def delete_record(self, session_id: int, student_id: int) -> None:
        self._attendance_repo.delete(session_id=session_id, student_id=student_id)

    def _validate_record(self, session_id: int, student_id: int, status: str) -> None:
        if session_id <= 0 or student_id <= 0:
            raise ValueError("session_id and student_id must be > 0")

        valid_statuses = [e.value for e in AttendanceStatus]
        if status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}, got '{status}'")

        session = self._session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found.")
        if not self._enrollment_repo.get_by_id(session.class_id, student_id):
            raise ValueError("Student is not enrolled in this class.")
    