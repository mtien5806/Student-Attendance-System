from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from src.models.enums import (
    Role,
    SessionStatus,
    AttendanceStatus,
    RequestType,
    RequestStatus,
)
from src.utils.security import hash_password
from src.utils.time_utils import now

DB_PATH = Path("data") / "sas.db"


def get_conn(path: Optional[Path] = None) -> sqlite3.Connection:
    """Open SQLite connection with common PRAGMAs enabled."""
    db_path = path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db() -> None:
    """
    Initialize DB schema + indexes + seed demo data.

    Note: Adjust columns if your Stage 2 design has extra fields,
    but this schema is safe and supports all use cases.
    """
    conn = get_conn()
    cur = conn.cursor()

    # --- Schema (with constraints + ON DELETE rules) ---
    cur.executescript(
        f"""
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT NOT NULL UNIQUE,
            full_name       TEXT NOT NULL,
            role            TEXT NOT NULL CHECK (role IN ('{Role.STUDENT.value}','{Role.LECTURER.value}','{Role.ADMIN.value}')),
            password_hash   TEXT NOT NULL,
            failed_attempts INTEGER NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
            locked_until    TEXT NULL
        );

        CREATE TABLE IF NOT EXISTS classes (
            class_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code  TEXT NOT NULL UNIQUE,
            class_name  TEXT NOT NULL,
            lecturer_id INTEGER NOT NULL,
            FOREIGN KEY (lecturer_id) REFERENCES users(user_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            class_id   INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            PRIMARY KEY (class_id, student_id),
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS attendance_sessions (
            session_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id     INTEGER NOT NULL,
            session_date TEXT NOT NULL,    -- YYYY-MM-DD
            start_time   TEXT NOT NULL,    -- HH:MM
            duration_min INTEGER NOT NULL CHECK (duration_min > 0),
            pin_enabled  INTEGER NOT NULL DEFAULT 0 CHECK (pin_enabled IN (0,1)),
            pin_code     TEXT NULL,
            status       TEXT NOT NULL CHECK (status IN ('{SessionStatus.OPEN.value}','{SessionStatus.CLOSED.value}')),
            created_at   TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            UNIQUE (class_id, session_date, start_time)
        );

        CREATE TABLE IF NOT EXISTS attendance_records (
            record_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id    INTEGER NOT NULL,
            student_id    INTEGER NOT NULL,
            status        TEXT NOT NULL CHECK (status IN ('{AttendanceStatus.PRESENT.value}',
                                                         '{AttendanceStatus.LATE.value}',
                                                         '{AttendanceStatus.ABSENT.value}',
                                                         '{AttendanceStatus.EXCUSED.value}')),
            checkin_time  TEXT NULL,
            note          TEXT NULL,
            UNIQUE (session_id, student_id),
            FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS absence_requests (
            request_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id       INTEGER NOT NULL,
            session_id       INTEGER NOT NULL,
            request_type     TEXT NOT NULL CHECK (request_type IN ('{RequestType.ABSENT.value}','{RequestType.LATE.value}')),
            reason           TEXT NOT NULL,
            evidence_path    TEXT NULL,
            status           TEXT NOT NULL CHECK (status IN ('{RequestStatus.PENDING.value}',
                                                            '{RequestStatus.APPROVED.value}',
                                                            '{RequestStatus.REJECTED.value}')),
            lecturer_comment TEXT NULL,
            created_at       TEXT NOT NULL,
            updated_at       TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS warnings (
            warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            class_id   INTEGER NOT NULL,
            message    TEXT NOT NULL,
            created_at TEXT NOT NULL,
            seen       INTEGER NOT NULL DEFAULT 0 CHECK (seen IN (0,1)),
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
        );
        """
    )

    # --- Indexes (performance) ---
    cur.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_records_session_id ON attendance_records(session_id);
        CREATE INDEX IF NOT EXISTS idx_records_student_id ON attendance_records(student_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_class_date ON attendance_sessions(class_id, session_date);
        CREATE INDEX IF NOT EXISTS idx_requests_session_status ON absence_requests(session_id, status);
        """
    )

    # --- Seed demo data (only if empty users) ---
    n_users = cur.execute("SELECT COUNT(*) AS n FROM users;").fetchone()["n"]
    if n_users == 0:
        pw = hash_password("123456").value  # demo password

        cur.execute(
            "INSERT INTO users(username, full_name, role, password_hash) VALUES (?,?,?,?)",
            ("admin1", "Admin One", Role.ADMIN.value, pw),
        )
        cur.execute(
            "INSERT INTO users(username, full_name, role, password_hash) VALUES (?,?,?,?)",
            ("lect1", "Lecturer One", Role.LECTURER.value, pw),
        )
        cur.execute(
            "INSERT INTO users(username, full_name, role, password_hash) VALUES (?,?,?,?)",
            ("stu1", "Student One", Role.STUDENT.value, pw),
        )
        cur.execute(
            "INSERT INTO users(username, full_name, role, password_hash) VALUES (?,?,?,?)",
            ("stu2", "Student Two", Role.STUDENT.value, pw),
        )

        lecturer_id = cur.execute("SELECT user_id FROM users WHERE username='lect1'").fetchone()["user_id"]
        cur.execute(
            "INSERT INTO classes(class_code, class_name, lecturer_id) VALUES (?,?,?)",
            ("CSE101", "Intro to CS", lecturer_id),
        )
        class_id = cur.execute("SELECT class_id FROM classes WHERE class_code='CSE101'").fetchone()["class_id"]

        stu1_id = cur.execute("SELECT user_id FROM users WHERE username='stu1'").fetchone()["user_id"]
        stu2_id = cur.execute("SELECT user_id FROM users WHERE username='stu2'").fetchone()["user_id"]
        cur.executemany(
            "INSERT INTO enrollments(class_id, student_id) VALUES (?,?)",
            [(class_id, stu1_id), (class_id, stu2_id)],
        )

        # Create 1 demo OPEN session
        cur.execute(
            """
            INSERT INTO attendance_sessions(
                class_id, session_date, start_time, duration_min,
                pin_enabled, pin_code, status, created_at
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (class_id, "2026-01-01", "09:00", 60, 0, None, SessionStatus.OPEN.value, now().isoformat()),
        )

    conn.commit()
    conn.close()
