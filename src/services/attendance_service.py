from __future__ import annotations

from typing import Optional, Any
from datetime import datetime

from src.models.enums import AttendanceStatus, SessionStatus
from src.utils.validators import validate_pin, validate_date_range
from src.repositories.session_repo import SessionRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.db import get_conn


class AttendanceService:
    """UC02 Take Attendance; UC03 View Attendance; UC07 Record Attendance."""

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

        # Student must be enrolled in the class
        if not self.enrollment_repo.get_by_id(session.class_id, student_id):
            raise ValueError("You are not enrolled in this class.")

        # PIN validation if enabled
        if int(session.pin_enabled) == 1:
            if not pin_input:
                raise ValueError("PIN is required.")
            validate_pin(pin_input)
            if pin_input != (session.pin_code or ""):
                raise ValueError("Invalid PIN.")

        # Prevent duplicate
        if self.attendance_repo.get_by_session_student(session_id, student_id):
            raise ValueError("Already checked-in.")

        now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.attendance_repo.create(
            session_id=session_id,
            student_id=student_id,
            status=AttendanceStatus.PRESENT.value,
            checkin_time=now_s,
            note=None,
        )

    # -----------------------
    # UC03: View Attendance
    # -----------------------
    def list_student_attendance(
        self,
        student_id: int,
        *,
        class_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        validate_date_range(date_from, date_to)

        conn = get_conn()
        params: list[Any] = [student_id]
        where = ["ar.student_id = ?"]

        if class_id is not None:
            where.append("s.class_id = ?")
            params.append(class_id)
        if date_from is not None:
            where.append("s.session_date >= ?")
            params.append(date_from)
        if date_to is not None:
            where.append("s.session_date <= ?")
            params.append(date_to)

        rows = conn.execute(
            f"""
            SELECT
                ar.session_id,
                s.session_date,
                s.start_time,
                s.class_id,
                ar.status,
                COALESCE(ar.note,'-') AS note
            FROM attendance_records ar
            JOIN attendance_sessions s ON ar.session_id = s.session_id
            WHERE {' AND '.join(where)}
            ORDER BY s.session_date DESC, s.start_time DESC
            """,
            tuple(params),
        ).fetchall()
        conn.close()

        return [dict(r) for r in rows]

    # -----------------------
    # UC07: Lecturer record attendance
    # -----------------------
    def update_status(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> None:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found.")
        if session.status == SessionStatus.CLOSED.value:
            raise ValueError("Cannot update attendance. Session is closed.")

        # Student must be enrolled
        if not self.enrollment_repo.get_by_id(session.class_id, student_id):
            raise ValueError("Student is not enrolled in this class.")

        allowed = {s.value for s in AttendanceStatus}
        if status not in allowed:
            raise ValueError(f"Invalid status. Allowed: {', '.join(sorted(allowed))}.")

        rec = self.attendance_repo.get_by_session_student(session_id, student_id)
        if rec:
            self.attendance_repo.update(session_id, student_id, status=status, note=note)
        else:
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
            rec = self.attendance_repo.get_by_session_student(session_id, e.student_id)
            if rec:
                self.attendance_repo.update(session_id, e.student_id, status=AttendanceStatus.PRESENT.value)
            else:
                self.attendance_repo.create(
                    session_id=session_id,
                    student_id=e.student_id,
                    status=AttendanceStatus.PRESENT.value,
                    checkin_time=None,
                    note=None,
                )

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
                COALESCE(ar.status, ?) AS status
            FROM enrollments e
            JOIN users u ON e.student_id = u.user_id
            LEFT JOIN attendance_records ar
                ON ar.session_id = ? AND ar.student_id = u.user_id
            WHERE e.class_id = ?
            ORDER BY u.full_name, u.username
            """,
            (AttendanceStatus.ABSENT.value, session_id, session.class_id),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
