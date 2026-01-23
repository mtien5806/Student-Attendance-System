from __future__ import annotations

from typing import Optional, Any
from datetime import datetime

from src.models.enums import AttendanceStatus
from src.repositories.session_repo import SessionRepository
from src.repositories.attendance_repo import AttendanceRepository


class AttendanceService:
    """UC02 Take Attendance; UC07 Record Attendance; UC03 View Attendance; UC10 Manage Attendance (skeleton)."""

    def __init__(self) -> None:
        self.attendance_repo = AttendanceRepository()

    def student_checkin(
        self,
        student_id: int,
        session_id: int,
        pin_input: Optional[str]
    ) -> None:
        session = SessionRepository.get_by_id(session_id)
        if session is None:
            raise ValueError("Session does not exist")

        if session.status != "OPEN":
            raise ValueError("Session is not open")

        if session.pin_enabled:
            if not pin_input or pin_input != session.pin:
                raise ValueError("Invalid PIN")

        existed = AttendanceRepository.get_by_session_and_student(
            session_id=session_id,
            student_id=student_id
        )
        if existed:
            raise ValueError("Already checked in")

        AttendanceRepository.create(
            session_id=session_id,
            student_id=student_id,
            status=AttendanceStatus.present.value
            checkin_time=datetime.now()
        )

    # UC03
    def list_student_attendance(
        self,
        student_id: int,
        class_id=None,
        date_from=None,
        date_to=None
    ):
        return self.attendance_repo.list_by_filter(
            student_id=student_id,
            class_id=class_id,
            date_from=date_from,
            date_to=date_to,
        )
    #uc11
    def list_warnings(self, student_id: int) -> list[dict[str, Any]]:
        """
        UC11: Student xem danh sách cảnh báo
        Warning = ABSENT hoặc LATE
        """
        if student_id <= 0:
            raise ValueError("student_id must be > 0")

        records = self.attendance_repo.list_by_filter(student_id=student_id)

        warnings = []
        for r in records:
            if r.status in (
                AttendanceStatus.ABSENT.value,
                AttendanceStatus.LATE.value,
            ):
                warnings.append(
                    {
                        "record_id": r.record_id,
                        "session_id": r.session_id,
                        "status": r.status,
                        "checkin_time": r.checkin_time,
                        "note": r.note,
                    }
                )

        return warnings