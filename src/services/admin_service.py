from __future__ import annotations

from typing import Optional, Any


class AdminService:
    """UC05 Search Attendance; UC10 Manage Attendance (skeleton)."""

    def search_attendance(
        self,
        *,
        student_id: Optional[int] = None,
        session_id: Optional[int] = None,
        class_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # TODO: query attendance_records with filters
        raise NotImplementedError("search_attendance not implemented yet.")

    def add_record(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> None:
        # TODO: insert record into attendance_records
        raise NotImplementedError("add_record not implemented yet.")

    def edit_record(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> None:
        # TODO: update record status/note
        raise NotImplementedError("edit_record not implemented yet.")

    def delete_record(self, session_id: int, student_id: int) -> None:
        # TODO: delete record
        raise NotImplementedError("delete_record not implemented yet.")
