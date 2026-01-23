from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from src.models.enums import AttendanceStatus
from src.repositories.db import get_conn
from src.utils.validators import validate_date_range


@dataclass(frozen=True)
class AttendanceSearchFilters:
    """Filters for UC05 Search Attendance."""
    student_id: Optional[int] = None
    session_id: Optional[int] = None
    class_id: Optional[int] = None
    date_from: Optional[str] = None  # YYYY-MM-DD
    date_to: Optional[str] = None    # YYYY-MM-DD


class AdminService:
    """UC05 Search Attendance; UC10 Manage Attendance."""

    def search_attendance(
        self,
        *,
        student_id: Optional[int] = None,
        session_id: Optional[int] = None,
        class_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        UC05 Search Attendance (spec 8.7.1)

        Supports filters:
        - StudentID
        - SessionID
        - Course/Class (class_id)
        - Date range (session_date from/to)
        Returns detailed rows for UI printing.
        """
        date_from, date_to = validate_date_range(date_from, date_to)

        clauses: list[str] = []
        params: list[Any] = []

        if student_id is not None:
            clauses.append("ar.student_id = ?")
            params.append(student_id)
        if session_id is not None:
            clauses.append("ar.session_id = ?")
            params.append(session_id)
        if class_id is not None:
            clauses.append("s.class_id = ?")
            params.append(class_id)
        if date_from is not None:
            clauses.append("s.session_date >= ?")
            params.append(date_from)
        if date_to is not None:
            clauses.append("s.session_date <= ?")
            params.append(date_to)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        sql = f"""
        SELECT
            ar.record_id, ar.session_id, ar.student_id, ar.status, ar.checkin_time, ar.note,
            s.class_id, s.session_date, s.start_time, s.status AS session_status,
            c.class_code, c.class_name,
            stu.username AS student_username, stu.full_name AS student_name
        FROM attendance_records ar
        JOIN attendance_sessions s ON ar.session_id = s.session_id
        JOIN classes c ON s.class_id = c.class_id
        JOIN users stu ON ar.student_id = stu.user_id
        {where}
        ORDER BY s.session_date DESC, s.start_time DESC, c.class_code, stu.full_name
        """

        conn = get_conn()
        rows = conn.execute(sql, tuple(params)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ---------- UC10 Manage Attendance ----------

    def add_record(
        self,
        session_id: int,
        student_id: int,
        status: str,
        note: Optional[str] = None,
        checkin_time: Optional[str] = None,
    ) -> int:
        """
        UC10.1 Add missing attendance record
        Enforces:
        - Valid status
        - Session must exist
        - Student must exist
        - Student must be enrolled in class of session
        """
        self._validate_attendance_status(status)

        conn = get_conn()

        s = conn.execute(
            "SELECT class_id FROM attendance_sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
        if not s:
            conn.close()
            raise ValueError("Session ID not found.")

        u = conn.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (student_id,),
        ).fetchone()
        if not u:
            conn.close()
            raise ValueError("Student ID not found.")

        class_id = s["class_id"]
        enrolled = conn.execute(
            "SELECT 1 FROM enrollments WHERE class_id=? AND student_id=?",
            (class_id, student_id),
        ).fetchone()
        if not enrolled:
            conn.close()
            raise ValueError("Student is not enrolled in this class.")

        try:
            cur = conn.execute(
                """
                INSERT INTO attendance_records(session_id, student_id, status, checkin_time, note)
                VALUES (?,?,?,?,?)
                """,
                (session_id, student_id, status, checkin_time, note),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def edit_record(
        self,
        session_id: int,
        student_id: int,
        status: str,
        note: Optional[str] = None,
        checkin_time: Optional[str] = None,
    ) -> None:
        """
        UC10.2 Edit attendance status
        Must already exist; otherwise admin should use Add.
        """
        self._validate_attendance_status(status)

        conn = get_conn()
        row = conn.execute(
            "SELECT record_id FROM attendance_records WHERE session_id=? AND student_id=?",
            (session_id, student_id),
        ).fetchone()
        if not row:
            conn.close()
            raise ValueError("Attendance record not found for this SessionID and StudentID.")

        fields: list[str] = ["status=?"]
        params: list[Any] = [status]

        if note is not None:
            fields.append("note=?")
            params.append(note)
        if checkin_time is not None:
            fields.append("checkin_time=?")
            params.append(checkin_time)

        params.extend([session_id, student_id])

        conn.execute(
            f"UPDATE attendance_records SET {', '.join(fields)} WHERE session_id=? AND student_id=?",
            tuple(params),
        )
        conn.commit()
        conn.close()

    def delete_record(self, session_id: int, student_id: int) -> None:
        """
        UC10.3 Delete duplicated/incorrect record

        DB schema already prevents duplicates by UNIQUE(session_id, student_id).
        So this deletes the single record for that pair (correct behavior for 'incorrect').
        """
        conn = get_conn()
        conn.execute(
            "DELETE FROM attendance_records WHERE session_id=? AND student_id=?",
            (session_id, student_id),
        )
        conn.commit()
        conn.close()

    # ---------- helpers ----------

    @staticmethod
    def _validate_attendance_status(status: str) -> None:
        allowed = {s.value for s in AttendanceStatus}
        if status not in allowed:
            raise ValueError(f"Invalid status. Allowed: {', '.join(sorted(allowed))}.")
