from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.models.enums import RequestType


@dataclass
class SubmitRequestInput:
    student_id: int
    session_id: int
    request_type: RequestType
    reason: str
    evidence_path: Optional[str] = None


class RequestService:
    """UC04 Submit request; UC08 Approve; UC09 Reject (skeleton)."""

    def submit_request(self, data: SubmitRequestInput) -> int:
        if not data.reason or not data.reason.strip():
            raise ValueError("Reason is required.")
        # TODO: insert into absence_requests status=PENDING and return request_id
        raise NotImplementedError("submit_request not implemented yet.")

    def approve(self, request_id: int, lecturer_comment: Optional[str] = None) -> None:
        # TODO:
        # - set request status APPROVED
        # - update attendance record to Excused
        raise NotImplementedError("approve not implemented yet.")

    def reject(self, request_id: int, lecturer_comment: Optional[str] = None) -> None:
        # TODO:
        # - set request status REJECTED
        # - update attendance record to Absent (or keep rule)
        raise NotImplementedError("reject not implemented yet.")
