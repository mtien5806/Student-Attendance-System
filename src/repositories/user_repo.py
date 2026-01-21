from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from src.repositories.db import get_conn


@dataclass
class UserRow:
    user_id: int
    username: str
    full_name: str
    role: str
    password_hash: str
    failed_attempts: int
    locked_until: Optional[str]


class UserRepo:
    """DB operations for table `users`."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._external_conn = conn

    def _conn(self) -> sqlite3.Connection:
        return self._external_conn or get_conn()

    def get_by_username(self, username: str) -> Optional[UserRow]:
        conn = self._conn()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if self._external_conn is None:
            conn.close()
        if not row:
            return None
        return UserRow(**dict(row))

    def update_failed_attempts(self, user_id: int, failed_attempts: int) -> None:
        conn = self._conn()
        conn.execute("UPDATE users SET failed_attempts=? WHERE user_id=?", (failed_attempts, user_id))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def set_lock(self, user_id: int, locked_until_iso: Optional[str]) -> None:
        conn = self._conn()
        conn.execute("UPDATE users SET locked_until=? WHERE user_id=?", (locked_until_iso, user_id))
        conn.commit()
        if self._external_conn is None:
            conn.close()

    def reset_login_state(self, user_id: int) -> None:
        conn = self._conn()
        conn.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE user_id=?", (user_id,))
        conn.commit()
        if self._external_conn is None:
            conn.close()
