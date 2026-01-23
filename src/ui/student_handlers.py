from __future__ import annotations

from src.models.enums import RequestType
from src.services.attendance_service import AttendanceService
from src.services.request_service import RequestService, SubmitRequestInput
from src.services.warning_service import WarningService
from src.ui.menus import show_student_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_yes_no


def _prompt_int(label: str) -> int:
    while True:
        v = prompt_text(label)
        try:
            return int(v)
        except ValueError:
            print("Invalid number. Please try again.")


def run_student_dashboard(user) -> None:
    attendance_service = AttendanceService()
    request_service = RequestService()
    warning_service = WarningService()

    while True:
        warn_count = warning_service.count_warnings_for_student(user.user_id)
        pending_req = request_service.count_pending_for_student(user.user_id)

        print("\n[STUDENT DASHBOARD]")
        print(f"User: {user.full_name} (ID: {user.user_id})")
        print(f"Warnings: {warn_count} | Pending Requests: {pending_req}")
        print("-" * 50)
        show_student_menu()
        print("-" * 50)

        c = prompt_choice("Selection: ")

        if c == "0":
            return
        elif c == "1":
            _ui_take_attendance(attendance_service, user.user_id)
        elif c == "2":
            _ui_view_attendance(attendance_service, user.user_id)
        elif c == "3":
            _ui_submit_request(request_service, user.user_id)
        elif c == "4":
            _ui_view_warnings(warning_service, user.user_id)
        else:
            print("Invalid selection. Please try again.")


def _ui_take_attendance(attendance_service: AttendanceService, student_id: int) -> None:
    print("\n[TAKE ATTENDANCE]")
    session_id = _prompt_int("Enter Session ID: ")
    pin = prompt_text("Enter PIN (if required): ")
    if pin == "":
        pin = None
    try:
        attendance_service.student_checkin(student_id, session_id, pin)
        print("Check-in successful.")
    except Exception as e:
        print(f"Check-in failed: {e}")


def _ui_view_attendance(attendance_service: AttendanceService, student_id: int) -> None:
    print("\n[VIEW ATTENDANCE]")
    class_id_txt = prompt_text("Enter Course/Class ID (or leave blank to list all): ")
    class_id = int(class_id_txt) if class_id_txt else None
    date_from = prompt_text("From (YYYY-MM-DD) (optional): ") or None
    date_to = prompt_text("To (YYYY-MM-DD) (optional): ") or None

    try:
        rows = attendance_service.list_student_attendance(
            student_id,
            class_id=class_id,
            date_from=date_from,
            date_to=date_to,
        )
        if not rows:
            print("No attendance records.")
            return

        print("SessionID | Date       | Time  | Status   | Note")
        print("-" * 70)
        summary = {"Present": 0, "Late": 0, "Absent": 0, "Excused": 0}
        for r in rows:
            st = r["status"]
            summary[st] = summary.get(st, 0) + 1
            note = r.get("note") or "-"
            print(f"{r['session_id']:<8} | {r['session_date']} | {r['start_time']:<5} | {st:<8} | {note}")
        print("-" * 70)
        print(f"Summary: Present={summary.get('Present',0)}, Late={summary.get('Late',0)}, Absent={summary.get('Absent',0)}")
    except Exception as e:
        print(f"Error: {e}")


def _ui_submit_request(request_service: RequestService, student_id: int) -> None:
    print("\n[SUBMIT REQUEST]")
    session_id = _prompt_int("Enter Session ID: ")
    print("Request Type: 1. Absent   2. Late")
    t = prompt_choice("Selection: ")
    req_type = RequestType.ABSENT if t == "1" else RequestType.LATE if t == "2" else None
    if req_type is None:
        print("Invalid selection.")
        return
    reason = prompt_text("Reason (text): ")
    evidence = prompt_text("Optional Evidence File Path (leave blank if none): ") or None
    if not prompt_yes_no("Confirm submission (Y/N): "):
        print("Cancelled.")
        return
    try:
        rid = request_service.submit_request(
            SubmitRequestInput(
                student_id=student_id,
                session_id=session_id,
                request_type=req_type,
                reason=reason,
                evidence_path=evidence,
            )
        )
        print(f"Request submitted. RequestID={rid} (status=PENDING).")
    except Exception as e:
        print(f"Error: {e}")


def _ui_view_warnings(warning_service: WarningService, student_id: int) -> None:
    print("\n[WARNINGS]")
    warnings = warning_service.list_warnings_for_student(student_id)
    if not warnings:
        print("No warnings.")
        return

    print("WarningID | Date       | ClassID | Message")
    print("-" * 80)
    for w in warnings:
        created = w.get("created_at","")[:10]
        print(f"{w['warning_id']:<9} | {created:<10} | {w['class_id']:<7} | {w['message']}")
    print("-" * 80)

    # mark seen (optional)
    wid = prompt_text("Enter WarningID to mark as seen (or blank to return): ").strip()
    if wid:
        try:
            warning_service.mark_seen(int(wid))
            print("Marked as seen.")
        except Exception as e:
            print(f"Error: {e}")
