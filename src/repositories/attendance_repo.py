from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from src.repositories.db import get_conn


@dataclass
class AttendanceRow:
    record_id: int
    session_id: int
    student_id: int
    status: str
    checkin_time: Optional[str]
    note: Optional[str]


class AttendanceRepo:
    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_id(self, record_id: int) -> Optional[AttendanceRow]:
        conn = self._conn()
        row = conn.execute("SELECT * FROM attendance_records WHERE record_id=?", (record_id,)).fetchone()
        if self._external_conn is None:
            conn.close()
        return AttendanceRow(**dict(row)) if row else None

    def get_by_session_student(self, session_id: int, student_id: int) -> Optional[AttendanceRow]:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM attendance_records WHERE session_id=? AND student_id=?",
            (session_id, student_id),
        ).fetchone()
        if self._external_conn is None:
            conn.close()
        return AttendanceRow(**dict(row)) if row else None

    def list_by_filter(
        self,
        *,
        session_id: int | None = None,
        student_id: int | None = None,
    ) -> list[AttendanceRow]:
        conn = self._conn()
        if session_id is not None:
            rows = conn.execute(
                "SELECT * FROM attendance_records WHERE session_id=? ORDER BY student_id",
                (session_id,),
            ).fetchall()
        elif student_id is not None:
            rows = conn.execute(
                "SELECT * FROM attendance_records WHERE student_id=? ORDER BY session_id DESC",
                (student_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM attendance_records ORDER BY session_id DESC").fetchall()

        if self._external_conn is None:
            conn.close()
        return [AttendanceRow(**dict(r)) for r in rows]

    def create(
        self,
        *,
        session_id: int,
        student_id: int,
        status: str,
        checkin_time: Optional[str] = None,
        note: Optional[str] = None,
    ) -> int:
        conn = self._conn()
        cur = conn.execute(
            """
            INSERT INTO attendance_records(session_id, student_id, status, checkin_time, note)
            VALUES (?,?,?,?,?)
            """,
            (session_id, student_id, status, checkin_time, note),
        )
        conn.commit()
        if self._external_conn is None:
            conn.close()
        return int(cur.lastrowid)

    def update(self, session_id: int, student_id: int, *, status: Optional[str] = None, checkin_time: Optional[str] = None, note: Optional[str] = None) -> None:
        fields, params = [], []
        if status is not None:
            fields.append("status=?")
            params.append(status)
        if checkin_time is not None:
            fields.append("checkin_time=?")
            params.append(checkin_time)
        if note is not None:
            fields.append("note=?")
            params.append(note)
        if not fields:
            return
        params.extend([session_id, student_id])

        conn = self._conn()
        conn.execute(
            f"UPDATE attendance_records SET {', '.join(fields)} WHERE session_id=? AND student_id=?",
            tuple(params),
        )
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def delete(self, session_id: int, student_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM attendance_records WHERE session_id=? AND student_id=?", (session_id, student_id))
        conn.commit()
        if self._external_conn is None:
            conn.close()
