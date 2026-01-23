from __future__ import annotations

from typing import Optional

from src.models.enums import AttendanceStatus
from src.services.admin_service import AdminService
from src.ui.menus import show_admin_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_yes_no


def _prompt_int(label: str, *, allow_blank: bool = False) -> Optional[int]:
    while True:
        raw = prompt_text(label)
        if allow_blank and raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Invalid number. Please try again.")


def _prompt_status() -> str:
    print("New Status: 1. Present  2. Late  3. Absent  4. Excused")
    while True:
        c = prompt_choice("Selection: ")
        mapping = {
            "1": AttendanceStatus.PRESENT.value,
            "2": AttendanceStatus.LATE.value,
            "3": AttendanceStatus.ABSENT.value,
            "4": AttendanceStatus.EXCUSED.value,
        }
        if c in mapping:
            return mapping[c]
        print("Invalid menu selection. Please try again.")


def run_admin_dashboard(*, admin_id: int, admin_name: str) -> None:
    svc = AdminService()

    while True:
        print("\n[ADMINISTRATOR DASHBOARD]")
        print(f"User: {admin_name} (ID: {admin_id})")
        print("-" * 50)
        show_admin_menu()
        print("-" * 50)

        sel = prompt_choice("Selection: ")

        if sel == "0":
            return
        if sel == "1":
            _search_attendance_ui(svc)
        elif sel == "2":
            _manage_attendance_ui(svc)
        else:
            print("Invalid menu selection. Please try again.")


def _search_attendance_ui(svc: AdminService) -> None:
    print("\n[SEARCH ATTENDANCE]")
    print("Search by: 1. StudentID  2. SessionID  3. Course/Class  4. Date Range  0. Back")
    choice = prompt_choice("Selection: ")
    if choice == "0":
        return

    student_id = session_id = class_id = None
    date_from = date_to = None

    if choice == "1":
        student_id = _prompt_int("Enter Student ID: ")
    elif choice == "2":
        session_id = _prompt_int("Enter Session ID: ")
    elif choice == "3":
        class_id = _prompt_int("Enter Course/Class ID: ")
    elif choice == "4":
        date_from = prompt_text("Enter From Date (YYYY-MM-DD): ") or None
        date_to = prompt_text("Enter To Date (YYYY-MM-DD): ") or None
    else:
        print("Invalid menu selection. Please try again.")
        return

    try:
        rows = svc.search_attendance(
            student_id=student_id,
            session_id=session_id,
            class_id=class_id,
            date_from=date_from,
            date_to=date_to,
        )
    except Exception as e:
        print(f"Error: {e}")
        return

    print("-" * 50)
    if not rows:
        print("No matching records.")
        return

    print("RecordID | SessionID | Class | Date | StudentID | StudentName | Status | Checkin | Note")
    print("-" * 50)
    for r in rows:
        print(
            f"{r['record_id']} | {r['session_id']} | {r['class_code']} | {r['session_date']} | "
            f"{r['student_id']} | {r['student_name']} | {r['status']} | {r.get('checkin_time') or ''} | {r.get('note') or ''}"
        )


def _manage_attendance_ui(svc: AdminService) -> None:
    while True:
        print("\n[MANAGE ATTENDANCE]")
        print("Actions:")
        print("1. Add missing attendance record")
        print("2. Edit attendance status")
        print("3. Delete duplicated/incorrect record")
        print("0. Back")
        print("-" * 50)

        sel = prompt_choice("Selection: ")

        if sel == "0":
            return
        if sel == "1":
            _manage_add(svc)
        elif sel == "2":
            _manage_edit(svc)
        elif sel == "3":
            _manage_delete(svc)
        else:
            print("Invalid menu selection. Please try again.")


def _manage_add(svc: AdminService) -> None:
    session_id = _prompt_int("Enter Session ID: ")
    student_id = _prompt_int("Enter Student ID: ")
    status = _prompt_status()
    note = prompt_text("Reason/Note (optional): ") or None
    if not prompt_yes_no("Confirm (Y/N): "):
        print("Cancelled.")
        return
    try:
        rid = svc.add_record(session_id=session_id, student_id=student_id, status=status, note=note)
        print(f"Added record_id={rid}.")
    except Exception as e:
        print(f"Error: {e}")


def _manage_edit(svc: AdminService) -> None:
    session_id = _prompt_int("Enter Session ID: ")
    student_id = _prompt_int("Enter Student ID: ")
    status = _prompt_status()
    note = prompt_text("Reason/Note (optional): ") or None
    if not prompt_yes_no("Confirm (Y/N): "):
        print("Cancelled.")
        return
    try:
        svc.edit_record(session_id=session_id, student_id=student_id, status=status, note=note)
        print("Updated.")
    except Exception as e:
        print(f"Error: {e}")


def _manage_delete(svc: AdminService) -> None:
    session_id = _prompt_int("Enter Session ID: ")
    student_id = _prompt_int("Enter Student ID: ")
    if not prompt_yes_no("Confirm deletion (Y/N): "):
        print("Cancelled.")
        return
    try:
        svc.delete_record(session_id=session_id, student_id=student_id)
        print("Deleted (if existed).")
    except Exception as e:
        print(f"Error: {e}")
