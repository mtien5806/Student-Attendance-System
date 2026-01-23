from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from src.repositories.db import get_conn


@dataclass
class ClassRow:
    class_id: int
    class_code: str
    class_name: str
    lecturer_id: int


class ClassRepo:
    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_id(self, class_id: int) -> Optional[ClassRow]:
        conn = self._conn()
        row = conn.execute("SELECT * FROM classes WHERE class_id=?", (class_id,)).fetchone()
        if self._external_conn is None:
            conn.close()
        return ClassRow(**dict(row)) if row else None

    def list_by_filter(self, *, lecturer_id: Optional[int] = None) -> list[ClassRow]:
        conn = self._conn()
        if lecturer_id is None:
            rows = conn.execute("SELECT * FROM classes ORDER BY class_code").fetchall()
        else:
            rows = conn.execute("SELECT * FROM classes WHERE lecturer_id=? ORDER BY class_code", (lecturer_id,)).fetchall()
        if self._external_conn is None:
            conn.close()
        return [ClassRow(**dict(r)) for r in rows]

    def create(self, class_code: str, class_name: str, lecturer_id: int) -> int:
        conn = self._conn()
        cur = conn.execute(
            "INSERT INTO classes(class_code, class_name, lecturer_id) VALUES (?,?,?)",
            (class_code, class_name, lecturer_id),
        )
        conn.commit()
        if self._external_conn is None:
            conn.close()
        new_id = cur.lastrowid
        if new_id is None:
            raise RuntimeError("Insert failed: lastrowid is None")
        return int(new_id)


    def update(self, class_id: int, *, class_code: Optional[str] = None, class_name: Optional[str] = None) -> None:
        fields, params = [], []
        if class_code is not None:
            fields.append("class_code=?")
            params.append(class_code)
        if class_name is not None:
            fields.append("class_name=?")
            params.append(class_name)
        if not fields:
            return
        params.append(class_id)
        conn = self._conn()
        conn.execute(f"UPDATE classes SET {', '.join(fields)} WHERE class_id=?", tuple(params))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def delete(self, class_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM classes WHERE class_id=?", (class_id,))
        conn.commit()
        if self._external_conn is None:
            conn.close()
