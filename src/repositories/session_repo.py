from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from src.repositories.db import get_conn


@dataclass
class SessionRow:
    session_id: int
    class_id: int
    session_date: str
    start_time: str
    duration_min: int
    pin_enabled: int
    pin_code: Optional[str]
    status: str
    created_at: str


class SessionRepo:
    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_id(self, session_id: int) -> Optional[SessionRow]:
        conn = self._conn()
        row = conn.execute("SELECT * FROM attendance_sessions WHERE session_id=?", (session_id,)).fetchone()
        if self._external_conn is None:
            conn.close()
        return SessionRow(**dict(row)) if row else None

    def list_by_filter(
        self,
        *,
        class_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        status: str | None = None,
    ) -> list[SessionRow]:
        clauses, params = [], []
        if class_id is not None:
            clauses.append("class_id=?")
            params.append(class_id)
        if status is not None:
            clauses.append("status=?")
            params.append(status)
        if date_from is not None:
            clauses.append("session_date >= ?")
            params.append(date_from)
        if date_to is not None:
            clauses.append("session_date <= ?")
            params.append(date_to)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT * FROM attendance_sessions {where} ORDER BY session_date DESC, start_time DESC"

        conn = self._conn()
        rows = conn.execute(sql, tuple(params)).fetchall()
        if self._external_conn is None:
            conn.close()
        return [SessionRow(**dict(r)) for r in rows]

    def create(
        self,
        *,
        class_id: int,
        session_date: str,
        start_time: str,
        duration_min: int,
        pin_enabled: int,
        pin_code: Optional[str],
        status: str,
        created_at: str,
    ) -> int:
        conn = self._conn()
        cur = conn.execute(
            """
            INSERT INTO attendance_sessions(
                class_id, session_date, start_time, duration_min,
                pin_enabled, pin_code, status, created_at
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (class_id, session_date, start_time, duration_min, pin_enabled, pin_code, status, created_at),
        )
        conn.commit()
        if self._external_conn is None:
            conn.close()
        new_id = cur.lastrowid
        if new_id is None:
            raise RuntimeError("Insert failed: lastrowid is None")
        return int(new_id)


    def update(self, session_id: int, *, status: Optional[str] = None, pin_code: Optional[str] = None) -> None:
        fields, params = [], []
        if status is not None:
            fields.append("status=?")
            params.append(status)
        if pin_code is not None:
            fields.append("pin_code=?")
            params.append(pin_code)
        if not fields:
            return
        params.append(session_id)

        conn = self._conn()
        conn.execute(f"UPDATE attendance_sessions SET {', '.join(fields)} WHERE session_id=?", tuple(params))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def delete(self, session_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM attendance_sessions WHERE session_id=?", (session_id,))
        conn.commit()
        if self._external_conn is None:
            conn.close()
