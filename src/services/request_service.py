from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

from src.models.enums import RequestType, RequestStatus, AttendanceStatus
from src.repositories.request_repo import RequestRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.db import get_conn


@dataclass
class SubmitRequestInput:
    student_id: int
    session_id: int
    request_type: RequestType
    reason: str
    evidence_path: Optional[str] = None


class RequestService:
    """UC04 Submit request; UC08 Approve; UC09 Reject."""

    def __init__(self) -> None:
        self.request_repo = RequestRepo()
        self.attendance_repo = AttendanceRepo()

    def submit_request(self, data: SubmitRequestInput) -> int:
        if not data.reason or not data.reason.strip():
            raise ValueError("Reason is required.")

        now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        request_id = self.request_repo.create(
            student_id=data.student_id,
            session_id=data.session_id,
            request_type=data.request_type.value,
            reason=data.reason.strip(),
            evidence_path=data.evidence_path,
            status=RequestStatus.PENDING.value,
            created_at=now_s,
            updated_at=now_s,
        )
        return request_id

    def list_pending_for_lecturer(self, lecturer_id: int) -> list[dict[str, Any]]:
        """
        Helper for lecturer UI:
        Get pending requests only for classes taught by lecturer.
        """
        conn = get_conn()
        rows = conn.execute(
            """
            SELECT
                r.request_id, r.student_id, r.session_id, r.request_type, r.reason, r.status, r.created_at,
                s.session_date, s.start_time,
                c.class_id, c.class_code, c.class_name,
                COALESCE(u.full_name, u.username) AS student_name
            FROM absence_requests r
            JOIN attendance_sessions s ON r.session_id = s.session_id
            JOIN classes c ON s.class_id = c.class_id
            JOIN users u ON r.student_id = u.user_id
            WHERE r.status = ? AND c.lecturer_id = ?
            ORDER BY r.created_at DESC
            """,
            (RequestStatus.PENDING.value, lecturer_id),
        ).fetchall()
        conn.close()
        return [dict(x) for x in rows]

    def approve(self, request_id: int, lecturer_comment: Optional[str] = None) -> None:
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise ValueError("Request not found.")

        now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.request_repo.update(
            request_id,
            status=RequestStatus.APPROVED.value,
            lecturer_comment=lecturer_comment,
            updated_at=now_s,
        )

        # Approved -> attendance becomes EXCUSED
        rec = self.attendance_repo.get_by_session_student(req.session_id, req.student_id)
        if rec:
            self.attendance_repo.update(req.session_id, req.student_id, status=AttendanceStatus.EXCUSED.value)
        else:
            self.attendance_repo.create(
                session_id=req.session_id,
                student_id=req.student_id,
                status=AttendanceStatus.EXCUSED.value,
                checkin_time=None,
                note="Excused by approved request",
            )

    def reject(self, request_id: int, lecturer_comment: Optional[str] = None) -> None:
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise ValueError("Request not found.")

        now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.request_repo.update(
            request_id,
            status=RequestStatus.REJECTED.value,
            lecturer_comment=lecturer_comment,
            updated_at=now_s,
        )

        # Rejected -> treat as unexcused (Absent)
        rec = self.attendance_repo.get_by_session_student(req.session_id, req.student_id)
        if rec:
            self.attendance_repo.update(req.session_id, req.student_id, status=AttendanceStatus.ABSENT.value)
        else:
            self.attendance_repo.create(
                session_id=req.session_id,
                student_id=req.student_id,
                status=AttendanceStatus.ABSENT.value,
                checkin_time=None,
                note="Request rejected",
            )
