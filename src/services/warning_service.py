from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.models.enums import AttendanceStatus
from src.repositories.db import get_conn
from src.repositories.warning_repo import WarningRepo
from src.utils.validators import validate_date_range

ABSENCE_THRESHOLD = 3
LATE_THRESHOLD = 3


class WarningService:
    """UC11: Warnings generated automatically when thresholds are exceeded."""

    def generate_warnings_for_class(
        self,
        *,
        class_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> int:
        """
        Generate warnings (avoid duplicates):
        - Missing record for a session counts as Absent
        - If Absent >= 3 -> create "Absence threshold reached (3)"
        - If Late >= 3 -> create "Late threshold reached (3)"
        Returns number of new warnings created.
        """
        date_from, date_to = validate_date_range(date_from, date_to)

        conn = get_conn()

        clauses, params = ["class_id=?"], [class_id]
        if date_from is not None:
            clauses.append("session_date>=?")
            params.append(date_from)
        if date_to is not None:
            clauses.append("session_date<=?")
            params.append(date_to)

        sessions = conn.execute(
            f"SELECT session_id FROM attendance_sessions WHERE {' AND '.join(clauses)}",
            tuple(params),
        ).fetchall()
        session_ids = [s["session_id"] for s in sessions]
        total_sessions = len(session_ids)

        students = conn.execute(
            "SELECT student_id FROM enrollments WHERE class_id=?",
            (class_id,),
        ).fetchall()
        student_ids = [r["student_id"] for r in students]

        rec_map = {}
        if session_ids:
            placeholders = ",".join(["?"] * len(session_ids))
            rows = conn.execute(
                f"SELECT session_id, student_id, status FROM attendance_records WHERE session_id IN ({placeholders})",
                tuple(session_ids),
            ).fetchall()
            rec_map = {(r["student_id"], r["session_id"]): r["status"] for r in rows}

        wrepo = WarningRepo(conn)
        existing = wrepo.list_by_filter(class_id=class_id)
        existing_set = {(w.student_id, w.class_id, w.message) for w in existing}

        created = 0
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for sid in student_ids:
            absent = total_sessions
            late = 0

            for sess_id in session_ids:
                status = rec_map.get((sid, sess_id))
                if status is None:
                    continue  # still absent
                absent -= 1
                if status == AttendanceStatus.ABSENT.value:
                    absent += 1
                if status == AttendanceStatus.LATE.value:
                    late += 1

            if absent >= ABSENCE_THRESHOLD:
                msg = f"Absence threshold reached ({ABSENCE_THRESHOLD})"
                key = (sid, class_id, msg)
                if key not in existing_set:
                    wrepo.create(student_id=sid, class_id=class_id, message=msg, created_at=now)
                    existing_set.add(key)
                    created += 1

            if late >= LATE_THRESHOLD:
                msg = f"Late threshold reached ({LATE_THRESHOLD})"
                key = (sid, class_id, msg)
                if key not in existing_set:
                    wrepo.create(student_id=sid, class_id=class_id, message=msg, created_at=now)
                    existing_set.add(key)
                    created += 1

        conn.commit()
        conn.close()
        return created
