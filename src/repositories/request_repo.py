from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from src.repositories.db import get_conn


@dataclass
class RequestRow:
    request_id: int
    student_id: int
    session_id: int
    request_type: str
    reason: str
    evidence_path: Optional[str]
    status: str
    lecturer_comment: Optional[str]
    created_at: str
    updated_at: str


class RequestRepo:
    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_id(self, request_id: int) -> Optional[RequestRow]:
        conn = self._conn()
        row = conn.execute("SELECT * FROM absence_requests WHERE request_id=?", (request_id,)).fetchone()
        if self._external_conn is None:
            conn.close()
        return RequestRow(**dict(row)) if row else None

    def list_by_filter(
        self,
        *,
        session_id: int | None = None,
        student_id: int | None = None,
        status: str | None = None,
    ) -> list[RequestRow]:
        clauses, params = [], []
        if session_id is not None:
            clauses.append("session_id=?")
            params.append(session_id)
        if student_id is not None:
            clauses.append("student_id=?")
            params.append(student_id)
        if status is not None:
            clauses.append("status=?")
            params.append(status)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT * FROM absence_requests {where} ORDER BY created_at DESC"

        conn = self._conn()
        rows = conn.execute(sql, tuple(params)).fetchall()
        if self._external_conn is None:
            conn.close()
        return [RequestRow(**dict(r)) for r in rows]

    def create(
        self,
        *,
        student_id: int,
        session_id: int,
        request_type: str,
        reason: str,
        evidence_path: Optional[str],
        status: str,
        created_at: str,
        updated_at: str,
    ) -> int:
        conn = self._conn()
        cur = conn.execute(
            """
            INSERT INTO absence_requests(
                student_id, session_id, request_type, reason, evidence_path,
                status, lecturer_comment, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (student_id, session_id, request_type, reason, evidence_path, status, None, created_at, updated_at),
        )
        conn.commit()
        if self._external_conn is None:
            conn.close()
        new_id = cur.lastrowid
        if new_id is None:
            raise RuntimeError("Insert failed: lastrowid is None")
        return int(new_id)


    def update(self, request_id: int, *, status: Optional[str] = None, lecturer_comment: Optional[str] = None, updated_at: Optional[str] = None) -> None:
        fields, params = [], []
        if status is not None:
            fields.append("status=?")
            params.append(status)
        if lecturer_comment is not None:
            fields.append("lecturer_comment=?")
            params.append(lecturer_comment)
        if updated_at is not None:
            fields.append("updated_at=?")
            params.append(updated_at)
        if not fields:
            return
        params.append(request_id)

        conn = self._conn()
        conn.execute(f"UPDATE absence_requests SET {', '.join(fields)} WHERE request_id=?", tuple(params))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def delete(self, request_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM absence_requests WHERE request_id=?", (request_id,))
        conn.commit()
        if self._external_conn is None:
            conn.close()
