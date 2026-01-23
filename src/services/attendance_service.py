from __future__ import annotations

from typing import Optional
from datetime import datetime

from src.models.enums import AttendanceStatus
from src.repositories.session_repo import SessionRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.enrollment_repo import EnrollmentRepo


class AttendanceService:
    """UC02 Take Attendance; UC07 Record Attendance; UC03 View Attendance; UC10 Manage Attendance (skeleton)."""

    def __init__(self):
        self.session_repo = SessionRepo()
        self.attendance_repo = AttendanceRepo()
        self.enrollment_repo = EnrollmentRepo()

    def student_checkin(self, student_id: int, session_id: int, pin_input: Optional[str]) -> None:
        # - validate session exists & OPEN
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session does not exist")

        if session.status != "OPEN":
            raise ValueError("Session is not open")

        # - if PIN enabled: validate pin_input
        if session.pin is not None:
            if not pin_input or pin_input != session.pin:
                raise ValueError("Invalid PIN")

        # - prevent duplicate check-in
        existing = self.attendance_repo.get(session_id, student_id)
        if existing:
            raise ValueError("Student already checked in")

        # - insert attendance_records
        self.attendance_repo.create({
            "session_id": session_id,
            "student_id": student_id,
            "status": AttendanceStatus.PRESENT,
            "checkin_time": datetime.now(),
            "note": None
        })

    def update_status(
        self,
        session_id: int,
        student_id: int,
        status: AttendanceStatus,
        note: Optional[str] = None
    ) -> None:
        # - lecturer/admin update attendance status
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status == "CLOSED":
            raise ValueError("Cannot update attendance. Session is closed")

        record = self.attendance_repo.get(session_id, student_id)
        if not record:
            raise ValueError("Attendance record not found")

        self.attendance_repo.update(session_id, student_id, {
            "status": status,
            "note": note
        })

    def mark_all_present(self, session_id: int) -> None:
        # - batch set all students in class(session) to Present
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status == "CLOSED":
            raise ValueError("Cannot mark attendance. Session is closed")

        students = self.enrollment_repo.list_students(session.class_id)

        for student in students:
            record = self.attendance_repo.get(session_id, student.id)

            if record:
                self.attendance_repo.update(session_id, student.id, {
                    "status": AttendanceStatus.PRESENT
                })
            else:
                self.attendance_repo.create({
                    "session_id": session_id,
                    "student_id": student.id,
                    "status": AttendanceStatus.PRESENT,
                    "checkin_time": None,
                    "note": None
                })
