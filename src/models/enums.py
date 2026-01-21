from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    STUDENT = "STUDENT"
    LECTURER = "LECTURER"
    ADMIN = "ADMIN"


class SessionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    LATE = "Late"
    ABSENT = "Absent"
    EXCUSED = "Excused"


class RequestType(str, Enum):
    ABSENT = "Absent"
    LATE = "Late"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
