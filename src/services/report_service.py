from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from src.models.enums import AttendanceStatus
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.class_repo import ClassRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.session_repo import SessionRepo
from src.services.warning_service import WarningService


class ReportService:
    """UC12 Summarize Attendance; UC13 Export Attendance Report to Excel."""

    def __init__(self) -> None:
        self._attendance_repo = AttendanceRepo()
        self._class_repo = ClassRepo()
        self._enrollment_repo = EnrollmentRepo()
        self._session_repo = SessionRepo()
        self._warning_service = WarningService()

    def summarize(
        self, class_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        UC12 (spec 8.6.4):
        StudentID | Present | Late | Absent | Attendance Rate

        Important rule:
        - Missing attendance record for a session is treated as Absent.
        """
        sessions = self._session_repo.list_by_filter(class_id=class_id, date_from=date_from, date_to=date_to)
        session_ids = [s.session_id for s in sessions]
        total_sessions = len(session_ids)

        enrollments = self._enrollment_repo.list_by_filter(class_id=class_id)
        student_ids = [e.student_id for e in enrollments]

        summaries: list[dict[str, Any]] = []
        for student_id in student_ids:
            present = late = excused = 0
            # start as absent for ALL sessions (missing record counts as absent)
            absent = total_sessions

            for session_id in session_ids:
                record = self._attendance_repo.get_by_session_student(session_id, student_id)
                if record is None:
                    continue
                # if there is a record, remove one default absent
                absent -= 1

                if record.status == AttendanceStatus.PRESENT.value:
                    present += 1
                elif record.status == AttendanceStatus.LATE.value:
                    late += 1
                elif record.status == AttendanceStatus.EXCUSED.value:
                    excused += 1
                elif record.status == AttendanceStatus.ABSENT.value:
                    absent += 1  # explicit absent

            attended = present + late + excused
            rate = (attended / total_sessions * 100.0) if total_sessions > 0 else 0.0

            summaries.append(
                {
                    "student_id": student_id,
                    "present": present,
                    "late": late,
                    "absent": absent,
                    "excused": excused,
                    "total_sessions": total_sessions,
                    "attendance_rate": round(rate, 2),
                }
            )

        # UC11: generate warnings automatically (thresholds)
        self._warning_service.generate_warnings_for_class(class_id=class_id, date_from=date_from, date_to=date_to)

        return summaries

    def export_excel(
        self,
        class_id: int,
        output_path: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
        """
        UC13 (spec 8.6.5):
        User enters output file path (e.g., reports/CSE101_Attendance.xlsx).

        We support:
        - If output_path ends with .xlsx -> treat as file path
        - Else -> treat as folder and auto name Attendance_<ClassCode>_<timestamp>.xlsx
        """
        class_info = self._class_repo.get_by_id(class_id)
        if not class_info:
            raise ValueError(f"Class {class_id} not found")

        class_code = class_info.class_code

        output_path = output_path.strip()
        if output_path.lower().endswith(".xlsx"):
            file_path = Path(output_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            folder = Path(output_path) if output_path else Path("reports")
            folder.mkdir(parents=True, exist_ok=True)
            file_path = folder / f"{class_code}_Attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        wb = Workbook()
        self._create_summary_sheet(wb, class_id, date_from, date_to)
        self._create_detail_sheet(wb, class_id, date_from, date_to)

        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])

        wb.save(str(file_path))
        return str(file_path)

    def _create_summary_sheet(self, wb: Workbook, class_id: int, date_from: Optional[str], date_to: Optional[str]) -> None:
        ws = wb.active
        ws.title = "Summary"

        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))

        headers = ["Student ID", "Present", "Late", "Absent", "Excused", "Attendance Rate (%)"]
        ws.append(headers)

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        summaries = self.summarize(class_id, date_from, date_to)
        for s in summaries:
            ws.append([s["student_id"], s["present"], s["late"], s["absent"], s["excused"], s["attendance_rate"]])

        for row_idx in range(2, ws.max_row + 1):
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row_idx, col_idx)
                cell.border = border
                cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.column_dimensions["A"].width = 15
        for col in ["B", "C", "D", "E", "F"]:
            ws.column_dimensions[col].width = 18

    def _create_detail_sheet(self, wb: Workbook, class_id: int, date_from: Optional[str], date_to: Optional[str]) -> None:
        ws = wb.create_sheet("Detail")

        header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))

        headers = ["Session ID", "Session Date", "Start Time", "Student ID", "Status", "Check-in Time", "Note"]
        ws.append(headers)

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        sessions = self._session_repo.list_by_filter(class_id=class_id, date_from=date_from, date_to=date_to)
        enrollments = self._enrollment_repo.list_by_filter(class_id=class_id)
        student_ids = [e.student_id for e in enrollments]

        for session in sessions:
            for student_id in student_ids:
                record = self._attendance_repo.get_by_session_student(session.session_id, student_id)
                if record is None:
                    # missing -> Absent (spec logic)
                    ws.append([session.session_id, session.session_date, session.start_time, student_id, AttendanceStatus.ABSENT.value, "", ""])
                else:
                    ws.append([
                        record.session_id,
                        session.session_date,
                        session.start_time,
                        record.student_id,
                        record.status,
                        record.checkin_time or "",
                        record.note or "",
                    ])

        for row_idx in range(2, ws.max_row + 1):
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row_idx, col_idx)
                cell.border = border
                cell.alignment = Alignment(horizontal="left", vertical="center")

        widths = {"A": 12, "B": 15, "C": 10, "D": 12, "E": 12, "F": 18, "G": 25}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
