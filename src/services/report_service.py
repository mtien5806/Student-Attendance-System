from __future__ import annotations

import os
from typing import Optional, Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from src.models.enums import AttendanceStatus
from src.utils.validators import validate_date_range
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.class_repo import ClassRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.session_repo import SessionRepo


class ReportService:
    """UC12 Summarize attendance; UC13 Export Excel."""

    def __init__(self) -> None:
        self._attendance_repo = AttendanceRepo()
        self._enrollment_repo = EnrollmentRepo()
        self._session_repo = SessionRepo()
        self._class_repo = ClassRepo()

    def summarize(self, class_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None) -> list[dict[str, Any]]:
        validate_date_range(date_from, date_to)

        enrollments = self._enrollment_repo.list_by_filter(class_id=class_id)
        sessions = self._session_repo.list_by_filter(class_id=class_id, date_from=date_from, date_to=date_to)
        session_ids = [s.session_id for s in sessions]

        summaries: list[dict[str, Any]] = []
        for e in enrollments:
            sid = e.student_id
            counts = {"student_id": sid, "present": 0, "late": 0, "absent": 0, "excused": 0}

            for sess_id in session_ids:
                rec = self._attendance_repo.get_by_session_student(sess_id, sid)
                if not rec:
                    counts["absent"] += 1
                    continue
                st = rec.status
                if st == AttendanceStatus.PRESENT.value:
                    counts["present"] += 1
                elif st == AttendanceStatus.LATE.value:
                    counts["late"] += 1
                elif st == AttendanceStatus.ABSENT.value:
                    counts["absent"] += 1
                elif st == AttendanceStatus.EXCUSED.value:
                    counts["excused"] += 1
                else:
                    counts["absent"] += 1

            counts["total"] = counts["present"] + counts["late"] + counts["absent"] + counts["excused"]
            summaries.append(counts)

        return summaries

    def export_excel(self, class_id: int, output_path: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> str:
        validate_date_range(date_from, date_to)

        class_info = self._class_repo.get_by_id(class_id)
        if not class_info:
            raise ValueError(f"Class {class_id} not found")

        # output_path can be folder or full file path
        if output_path.lower().endswith(".xlsx"):
            file_path = output_path
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        else:
            os.makedirs(output_path, exist_ok=True)
            file_path = os.path.join(output_path, f"Attendance_{class_info.class_code}.xlsx")

        wb = Workbook()
        # remove default later
        self._create_summary_sheet(wb, class_id, date_from, date_to)
        self._create_detail_sheet(wb, class_id, date_from, date_to)

        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])

        wb.save(file_path)
        return file_path

    def _style_header(self, ws, row_idx: int) -> None:
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))
        for cell in ws[row_idx]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

    def _create_summary_sheet(self, wb: Workbook, class_id: int, date_from: Optional[str], date_to: Optional[str]) -> None:
        ws = wb.active
        ws.title = "Summary"
        headers = ["Student ID", "Present", "Late", "Absent", "Excused", "Total"]
        ws.append(headers)
        self._style_header(ws, 1)

        for s in self.summarize(class_id, date_from, date_to):
            ws.append([s["student_id"], s["present"], s["late"], s["absent"], s["excused"], s["total"]])

        for col in ["A","B","C","D","E","F"]:
            ws.column_dimensions[col].width = 14

    def _create_detail_sheet(self, wb: Workbook, class_id: int, date_from: Optional[str], date_to: Optional[str]) -> None:
        ws = wb.create_sheet("Detail")
        headers = ["Session ID", "Date", "Time", "Student ID", "Status", "Note"]
        ws.append(headers)
        self._style_header(ws, 1)

        sessions = self._session_repo.list_by_filter(class_id=class_id, date_from=date_from, date_to=date_to)
        enrollments = self._enrollment_repo.list_by_filter(class_id=class_id)
        for sess in sessions:
            for e in enrollments:
                rec = self._attendance_repo.get_by_session_student(sess.session_id, e.student_id)
                status = rec.status if rec else AttendanceStatus.ABSENT.value
                note = rec.note if rec and rec.note else "-"
                ws.append([sess.session_id, sess.session_date, sess.start_time, e.student_id, status, note])

        for col in ["A","B","C","D","E","F"]:
            ws.column_dimensions[col].width = 16
