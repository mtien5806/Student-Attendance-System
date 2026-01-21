from __future__ import annotations

from typing import Optional, Any


class ReportService:
    """UC12 Summarize attendance; UC13 Export Excel (skeleton)."""

    def summarize(self, class_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None) -> list[dict[str, Any]]:
        # TODO: aggregate counts Present/Late/Absent/Excused per student
        raise NotImplementedError("summarize not implemented yet.")

    def export_excel(self, class_id: int, output_path: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> str:
        # TODO: use openpyxl to export summary + detail sheets to reports/
        raise NotImplementedError("export_excel not implemented yet.")
