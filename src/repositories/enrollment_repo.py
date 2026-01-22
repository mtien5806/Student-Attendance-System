from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from src.repositories.db import get_conn


@dataclass
class EnrollmentRow:
    class_id: int
    student_id: int


class EnrollmentRepo:
    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_id(self, class_id: int, student_id: int) -> EnrollmentRow | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM enrollments WHERE class_id=? AND student_id=?",
            (class_id, student_id),
        ).fetchone()
        if self._external_conn is None:
            conn.close()
        return EnrollmentRow(**dict(row)) if row else None

    def list_by_filter(self, *, class_id: int | None = None, student_id: int | None = None) -> list[EnrollmentRow]:
        conn = self._conn()
        if class_id is not None:
            rows = conn.execute("SELECT * FROM enrollments WHERE class_id=? ORDER BY student_id", (class_id,)).fetchall()
        elif student_id is not None:
            rows = conn.execute("SELECT * FROM enrollments WHERE student_id=? ORDER BY class_id", (student_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM enrollments ORDER BY class_id, student_id").fetchall()
        if self._external_conn is None:
            conn.close()
        return [EnrollmentRow(**dict(r)) for r in rows]

    def create(self, class_id: int, student_id: int) -> None:
        conn = self._conn()
        conn.execute("INSERT INTO enrollments(class_id, student_id) VALUES (?,?)", (class_id, student_id))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def delete(self, class_id: int, student_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM enrollments WHERE class_id=? AND student_id=?", (class_id, student_id))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def update(self, *args, **kwargs) -> None:
        # Enrollment typically doesn't need update (PK is composite)
        return
