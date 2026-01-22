from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from src.repositories.db import get_conn


@dataclass
class WarningRow:
    warning_id: int
    student_id: int
    class_id: int
    message: str
    created_at: str
    seen: int


class WarningRepo:
    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_id(self, warning_id: int) -> WarningRow | None:
        conn = self._conn()
        row = conn.execute("SELECT * FROM warnings WHERE warning_id=?", (warning_id,)).fetchone()
        if self._external_conn is None:
            conn.close()
        return WarningRow(**dict(row)) if row else None

    def list_by_filter(self, *, student_id: int | None = None, class_id: int | None = None, unseen_only: bool = False) -> list[WarningRow]:
        clauses, params = [], []
        if student_id is not None:
            clauses.append("student_id=?")
            params.append(student_id)
        if class_id is not None:
            clauses.append("class_id=?")
            params.append(class_id)
        if unseen_only:
            clauses.append("seen=0")

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT * FROM warnings {where} ORDER BY created_at DESC"

        conn = self._conn()
        rows = conn.execute(sql, tuple(params)).fetchall()
        if self._external_conn is None:
            conn.close()
        return [WarningRow(**dict(r)) for r in rows]

    def create(self, *, student_id: int, class_id: int, message: str, created_at: str) -> int:
        conn = self._conn()
        cur = conn.execute(
            "INSERT INTO warnings(student_id, class_id, message, created_at, seen) VALUES (?,?,?,?,0)",
            (student_id, class_id, message, created_at),
        )
        conn.commit()
        if self._external_conn is None:
            conn.close()
        return int(cur.lastrowid)

    def update(self, warning_id: int, *, seen: int) -> None:
        conn = self._conn()
        conn.execute("UPDATE warnings SET seen=? WHERE warning_id=?", (seen, warning_id))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def delete(self, warning_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM warnings WHERE warning_id=?", (warning_id,))
        conn.commit()
        if self._external_conn is None:
            conn.close()
