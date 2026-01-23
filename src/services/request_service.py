from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.models.enums import RequestType, AttendanceStatus
from src.repositories.request_repo import RequestRepo
from src.repositories.attendance_repo import AttendanceRepo


@dataclass
class SubmitRequestInput:
    student_id: int
    session_id: int
    request_type: RequestType
    reason: str
    evidence_path: Optional[str] = None


class RequestService:
    """UC04 Submit request; UC08 Approve; UC09 Reject (skeleton)."""

    def __init__(self):
        self.request_repo = RequestRepo()
        self.attendance_repo = AttendanceRepo()

    def submit_request(self, data: SubmitRequestInput) -> int:
        if not data.reason or not data.reason.strip():
            raise ValueError("Reason is required.")

        # ===== TODO IMPLEMENTATION =====
        request_id = self.request_repo.create({
            "student_id": data.student_id,
            "session_id": data.session_id,
            "request_type": data.request_type,
            "reason": data.reason,
            "evidence_path": data.evidence_path,
            "status": "PENDING"
        })

        return request_id

    def approve(self, request_id: int, lecturer_comment: Optional[str] = None) -> None:
        # ===== TODO IMPLEMENTATION =====
        request = self.request_repo.get_by_id(request_id)
        if not request:
            raise ValueError("Request not found")

        self.request_repo.update(request_id, {
            "status": "APPROVED",
            "lecturer_comment": lecturer_comment
        })

        self.attendance_repo.update(
            request.session_id,
            request.student_id,
            {"status": AttendanceStatus.EXCUSED}
        )

    def reject(self, request_id: int, lecturer_comment: Optional[str] = None) -> None:
        # ===== TODO IMPLEMENTATION =====
        request = self.request_repo.get_by_id(request_id)
        if not request:
            raise ValueError("Request not found")

        self.request_repo.update(request_id, {
            "status": "REJECTED",
            "lecturer_comment": lecturer_comment
        })

        self.attendance_repo.update(
            request.session_id,
            request.student_id,
            {"status": AttendanceStatus.ABSENT}
        )
