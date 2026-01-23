from __future__ import annotations

from typing import Optional, Any

from src.models.enums import AttendanceStatus
from src.repositories.attendance_repo import AttendanceRepo


class AdminService:
    """UC05 Search Attendance; UC10 Manage Attendance."""

    def __init__(self) -> None:
        self._attendance_repo = AttendanceRepo()

    def search_attendance(
        self,
        *,
        student_id: Optional[int] = None,
        session_id: Optional[int] = None,
        class_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """UC05: Search Attendance - Tìm theo StudentID/SessionID/Class/Date range."""
        records = self._attendance_repo.list_by_filter(
            student_id=student_id,
            session_id=session_id,
            class_id=class_id,
            date_from=date_from,
            date_to=date_to,
        )
        return [
            {
                "record_id": r.record_id,
                "session_id": r.session_id,
                "student_id": r.student_id,
                "status": r.status,
                "checkin_time": r.checkin_time,
                "note": r.note,
            }
            for r in records
        ]

    def add_record(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> int:
        """UC10: Add attendance record."""
        # Validate trước khi thêm
        errors = self._validate_record(session_id, student_id, status)
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
        
        return self._attendance_repo.create(
            session_id=session_id,
            student_id=student_id,
            status=status,
            note=note,
        )

    def edit_record(self, session_id: int, student_id: int, status: str, note: Optional[str] = None) -> None:
        """UC10: Edit attendance record - update status/note."""
        # Validate trước khi sửa
        errors = self._validate_record(session_id, student_id, status)
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
        
        self._attendance_repo.update(
            session_id=session_id,
            student_id=student_id,
            status=status,
            note=note,
        )

    def delete_record(self, session_id: int, student_id: int) -> None:
        """UC10: Delete attendance record."""
        self._attendance_repo.delete(session_id=session_id, student_id=student_id)

    def find_duplicates(self, session_id: int, student_id: int) -> list[dict[str, Any]]:
        """Tìm bản ghi trùng (cùng session + student) - để phát hiện data sai."""
        records = self._attendance_repo.list_by_filter(
            session_id=session_id,
            student_id=student_id,
        )
        
        # Nếu có >1 record cho cùng (session, student), đó là trùng
        if len(records) <= 1:
            return []
        
        return [
            {
                "record_id": r.record_id,
                "session_id": r.session_id,
                "student_id": r.student_id,
                "status": r.status,
                "checkin_time": r.checkin_time,
                "note": r.note,
            }
            for r in records
        ]

    def _validate_record(self, session_id: int, student_id: int, status: str) -> list[str]:
        """
        Validate dữ liệu attendance record.
        Trả về list lỗi (empty nếu hợp lệ).
        """
        errors = []
        
        if session_id <= 0:
            errors.append("session_id must be > 0")
        
        if student_id <= 0:
            errors.append("student_id must be > 0")
        
        # Check status hợp lệ
        valid_statuses = [e.value for e in AttendanceStatus]
        if status not in valid_statuses:
            errors.append(f"status must be one of {valid_statuses}, got '{status}'")
        
        return errors

    def get_record(self, session_id: int, student_id: int) -> Optional[dict[str, Any]]:
        """Lấy record bằng session_id + student_id."""
        record = self._attendance_repo.get_by_session_student(session_id, student_id)
        if not record:
            return None
        
        return {
            "record_id": record.record_id,
            "session_id": record.session_id,
            "student_id": record.student_id,
            "status": record.status,
            "checkin_time": record.checkin_time,
            "note": record.note,
        }

    def bulk_delete_duplicates(self, session_id: int, student_id: int, keep_record_id: int) -> int:
        """
        Xoá các bản ghi trùng, giữ lại 1 record (keep_record_id).
        Trả về số lượng bản ghi bị xoá.
        """
        duplicates = self.find_duplicates(session_id, student_id)
        deleted_count = 0
        
        for dup in duplicates:
            if dup["record_id"] != keep_record_id:
                self._attendance_repo.delete(session_id, student_id)
                deleted_count += 1
        
        return deleted_count
