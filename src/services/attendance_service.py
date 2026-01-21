from __future__ import annotations

from typing import Optional
from src.models.enums import AttendanceStatus


class AttendanceService:
    """UC02 Take Attendance; UC07 Record Attendance; UC03 View Attendance; UC10 Manage Attendance (skeleton)."""

    def student_checkin(self, student_id: int, session_id: int, pin_input: Optional[str]) -> None:
        # TODO:
        # - validate session exists & OPEN
        # - if PIN enabled: validate pin_input
        # - prevent duplicate check-in (unique session_id+student_id)
        # - insert attendance_records with status=Present and checkin_time
        raise NotImplementedError("student_checkin not implemented yet.")

    def update_status(self, session_id: int, student_id: int, status: AttendanceStatus, note: Optional[str] = None) -> None:
        # TODO: update attendance_records status/note (lecturer/admin)
        raise NotImplementedError("update_status not implemented yet.")

    def mark_all_present(self, session_id: int) -> None:
        # TODO: batch set all students in class(session) to Present
        raise NotImplementedError("mark_all_present not implemented yet.")
