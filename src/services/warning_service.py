from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.models.enums import AttendanceStatus
from src.repositories.warning_repo import WarningRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.session_repo import SessionRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.class_repo import ClassRepo


ABSENCE_THRESHOLD = 3  # from spec example "Absence threshold reached (3)"


class WarningService:
    """UC11 View Attendance Warning + auto-generate warnings when thresholds exceeded."""

    def __init__(self) -> None:
        self.warning_repo = WarningRepo()
        self.enrollment_repo = EnrollmentRepo()
        self.session_repo = SessionRepo()
        self.attendance_repo = AttendanceRepo()
        self.class_repo = ClassRepo()

    def list_warnings_for_student(self, student_id: int) -> list[dict]:
        warnings = self.warning_repo.list_by_filter(student_id=student_id)
        return [vars(w) for w in warnings]

    def count_warnings_for_student(self, student_id: int, *, unseen_only: bool = False) -> int:
        return len(self.warning_repo.list_by_filter(student_id=student_id, unseen_only=unseen_only))

    def mark_seen(self, warning_id: int) -> None:
        self.warning_repo.update(warning_id, seen=1)

    def evaluate_and_generate_for_class(self, class_id: int) -> int:
        """Run rule for a class: if a student reaches ABSENCE_THRESHOLD absences -> create warning.
        Returns number of new warnings created.
        """
        cls = self.class_repo.get_by_id(class_id)
        if not cls:
            return 0

        # All sessions for class
        sessions = self.session_repo.list_by_filter(class_id=class_id)
        session_ids = [s.session_id for s in sessions]

        enrollments = self.enrollment_repo.list_by_filter(class_id=class_id)
        created = 0
        for e in enrollments:
            student_id = e.student_id

            absent_count = 0
            for sid in session_ids:
                rec = self.attendance_repo.get_by_session_student(sid, student_id)
                # Missing record counts as Absent
                if not rec:
                    absent_count += 1
                elif rec.status == AttendanceStatus.ABSENT.value:
                    absent_count += 1

            if absent_count >= ABSENCE_THRESHOLD:
                msg = f"Absence threshold reached ({ABSENCE_THRESHOLD})"
                # avoid duplicates: if same message exists already for this student+class, don't add
                existing = self.warning_repo.list_by_filter(student_id=student_id, class_id=class_id)
                if any(w.message == msg for w in existing):
                    continue
                now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.warning_repo.create(student_id=student_id, class_id=class_id, message=msg, created_at=now_s)
                created += 1

        return created
