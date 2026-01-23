from __future__ import annotations

from typing import Optional, Any
from datetime import datetime

from src.models.enums import AttendanceStatus, SessionStatus
from src.repositories.session_repo import SessionRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.db import get_conn


class AttendanceService:
    """UC02 Take Attendance; UC07 Record Attendance."""

    def __init__(self) -> None:
        self.session_repo = SessionRepo()
        self.attendance_repo = AttendanceRepo()
        self.enrollment_repo = EnrollmentRepo()

    # -----------------------
    # UC02: Student check-in
    # -----------------------
    def student_checkin(self, student_id: int, session_id: int, pin_input: Optional[str]) -> None:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session does not exist.")

        if session.status != SessionStatus.OPEN.value:
            raise ValueError("Session is not open.")

        # student must be enrolled in the class of this session
        enrolled = self.enrollment_repo.get_by_id(session.class_id, student_id)
        if not enrolled:
            raise ValueError("You are not enrolled in this class.")

        # pin check if enabled
        if int(session.pin_enabled) == 1:
            if not pin_input or pin_input != (session.pin_code or ""):
                raise ValueError("Invalid PIN.")

        # prevent duplicate
        existing = self.attendance_repo.get_by_session_student(session_id, student_id)
        if existing:
            raise ValueError("Student already checked in.")

        now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.attendance_repo.create(
            session_id=session_id,
            student_id=student_id,
            status=AttendanceStatus.PRESENT.value,
            checkin_time=now_s,
            note=None,
        )

    # -----------------------
    # UC07: Lecturer record attendance
    # -----------------------
    def update_status(
        self,
        session_id: int,
        student_id: int,
        status: str,
        note: Optional[str] = None,
    ) -> None:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found.")

        if session.status == SessionStatus.CLOSED.value:
            raise ValueError("Cannot update attendance. Session is closed.")

        # lecturer should only update students in the class
        enrolled = self.enrollment_repo.get_by_id(session.class_id, student_id)
        if not enrolled:
            raise ValueError("Student is not enrolled in this class.")

        # ensure status is valid
        allowed = {s.value for s in AttendanceStatus}
        if status not in allowed:
            raise ValueError(f"Invalid status. Allowed: {', '.join(sorted(allowed))}.")

        record = self.attendance_repo.get_by_session_student(session_id, student_id)
        if record:
            self.attendance_repo.update(session_id, student_id, status=status, note=note)
        else:
            # create missing record (valid for UC07)
            self.attendance_repo.create(
                session_id=session_id,
                student_id=student_id,
                status=status,
                checkin_time=None,
                note=note,
            )

    def mark_all_present(self, session_id: int) -> None:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found.")

        if session.status == SessionStatus.CLOSED.value:
            raise ValueError("Cannot mark attendance. Session is closed.")

        enrollments = self.enrollment_repo.list_by_filter(class_id=session.class_id)
        for e in enrollments:
            student_id = e.student_id
            record = self.attendance_repo.get_by_session_student(session_id, student_id)
            if record:
                self.attendance_repo.update(session_id, student_id, status=AttendanceStatus.PRESENT.value)
            else:
                self.attendance_repo.create(
                    session_id=session_id,
                    student_id=student_id,
                    status=AttendanceStatus.PRESENT.value,
                    checkin_time=None,
                    note=None,
                )

    # tiện cho UI lecturer: lấy roster + status hiện tại
    def get_roster_for_session(self, session_id: int) -> list[dict[str, Any]]:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found.")

        conn = get_conn()
        rows = conn.execute(
            """
            SELECT
                u.user_id AS student_id,
                COALESCE(u.full_name, u.username) AS student_name,
                ar.status AS status
            FROM enrollments e
            JOIN users u ON e.student_id = u.user_id
            LEFT JOIN attendance_records ar
                ON ar.session_id = ? AND ar.student_id = u.user_id
            WHERE e.class_id = ?
            ORDER BY u.full_name, u.username
            """,
            (session_id, session.class_id),
        ).fetchall()
        conn.close()

        out = []
        for r in rows:
            out.append({
                "student_id": r["student_id"],
                "student_name": r["student_name"],
                "status": r["status"] or AttendanceStatus.ABSENT.value,
            })
        return out
