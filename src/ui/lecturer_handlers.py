from __future__ import annotations

from src.models.enums import AttendanceStatus, RequestType
from src.services.session_service import SessionService, CreateSessionInput
from src.services.attendance_service import AttendanceService
from src.services.request_service import RequestService
from src.services.report_service import ReportService
from src.services.warning_service import WarningService
from src.repositories.class_repo import ClassRepo
from src.ui.menus import show_lecturer_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_yes_no


def _prompt_int(label: str) -> int:
    while True:
        v = prompt_text(label)
        try:
            return int(v)
        except ValueError:
            print("Invalid number. Please try again.")


def _prompt_status() -> str:
    print("Status: 1. Present  2. Late  3. Absent  4. Excused")
    m = {
        "1": AttendanceStatus.PRESENT.value,
        "2": AttendanceStatus.LATE.value,
        "3": AttendanceStatus.ABSENT.value,
        "4": AttendanceStatus.EXCUSED.value,
    }
    while True:
        c = prompt_choice("Selection: ")
        if c in m:
            return m[c]
        print("Invalid selection. Try again.")


def run_lecturer_dashboard(user) -> None:
    session_service = SessionService()
    attendance_service = AttendanceService()
    request_service = RequestService()
    report_service = ReportService()
    warning_service = WarningService()
    class_repo = ClassRepo()

    while True:
        pending_count = request_service.count_pending_for_lecturer(user.user_id)

        print("\n[LECTURER DASHBOARD]")
        print(f"User: {user.full_name} (ID: {user.user_id})")
        print(f"Pending Requests: {pending_count}")
        print("-" * 50)
        show_lecturer_menu()
        print("-" * 50)

        c = prompt_choice("Selection: ")

        if c == "0":
            return
        if c == "1":
            _ui_create_session(session_service, class_repo, user.user_id)
        elif c == "2":
            _ui_record_attendance(attendance_service, session_service, warning_service)
        elif c == "3":
            _ui_process_requests(request_service, user.user_id)
        elif c == "4":
            _ui_summarize(report_service, class_repo, user.user_id)
        elif c == "5":
            _ui_export(report_service, class_repo, user.user_id)
        else:
            print("Invalid selection. Please try again.")


def _ui_create_session(session_service: SessionService, class_repo: ClassRepo, lecturer_id: int) -> None:
    print("\n[CREATE ATTENDANCE SESSION]")
    classes = class_repo.list_by_filter(lecturer_id=lecturer_id)
    if not classes:
        print("You have no classes.")
        return

    print("Your classes:")
    for c in classes:
        print(f"- ClassID={c.class_id} | {c.class_code} | {c.class_name}")

    class_id = _prompt_int("Enter Class ID: ")
    session_date = prompt_text("Enter Date (YYYY-MM-DD): ")
    start_time = prompt_text("Enter Start Time (HH:MM): ")
    duration = _prompt_int("Enter Duration (minutes): ")
    pin_enabled = prompt_yes_no("Enable PIN? (Y/N): ")
    pin_code = None
    if pin_enabled:
        pin_code = prompt_text("Enter PIN (4-6 digits) or leave blank to auto-generate: ") or None

    try:
        sid = session_service.create_session(
            CreateSessionInput(
                class_id=class_id,
                session_date=session_date,
                start_time=start_time,
                duration_min=duration,
                pin_enabled=pin_enabled,
                pin_code=pin_code,
                lecturer_id=lecturer_id,
            )
        )
        print(f"Session created successfully. SessionID={sid}")
    except Exception as e:
        print(f"Error: {e}")


def _ui_record_attendance(attendance_service: AttendanceService, session_service: SessionService, warning_service: WarningService) -> None:
    print("\n[RECORD ATTENDANCE]")
    session_id = _prompt_int("Enter Session ID: ")

    try:
        session = session_service.session_repo.get_by_id(session_id)
        if not session:
            print("Session not found.")
            return

        while True:
            print("\nActions:")
            print("1. View roster/status")
            print("2. Update one student status")
            print("3. Mark ALL Present")
            print("4. Close session")
            print("0. Back")
            sel = prompt_choice("Selection: ")

            if sel == "0":
                return

            if sel == "1":
                roster = attendance_service.get_roster_for_session(session_id)
                print("StudentID | StudentName | Status")
                print("-" * 60)
                for r in roster:
                    print(f"{r['student_id']} | {r['student_name']} | {r['status']}")
                continue

            if sel == "2":
                student_id = _prompt_int("Enter Student ID: ")
                status = _prompt_status()
                note = prompt_text("Note (optional): ") or None
                if not prompt_yes_no("Confirm (Y/N): "):
                    print("Cancelled.")
                    continue
                attendance_service.update_status(session_id, student_id, status, note=note)
                print("Updated.")
                continue

            if sel == "3":
                if not prompt_yes_no("Mark all present? (Y/N): "):
                    print("Cancelled.")
                    continue
                attendance_service.mark_all_present(session_id)
                print("Done.")
                continue

            if sel == "4":
                if not prompt_yes_no("Close this session? (Y/N): "):
                    print("Cancelled.")
                    continue
                session_service.close_session(session_id)
                # after close, run warning generation for that class
                warning_service.evaluate_and_generate_for_class(session.class_id)
                print("Session closed.")
                continue

            print("Invalid selection.")
    except Exception as e:
        print(f"Error: {e}")


def _ui_process_requests(request_service: RequestService, lecturer_id: int) -> None:
    print("\n[PROCESS REQUESTS]")
    pending = request_service.list_pending_for_lecturer(lecturer_id)
    if not pending:
        print("No pending requests.")
        return

    print("Pending Requests:")
    print("ReqID | Class | Date | Student | Type | Reason")
    print("-" * 90)
    for r in pending:
        print(f"{r['request_id']} | {r['class_code']} | {r['session_date']} {r['start_time']} | {r['student_name']} | {r['request_type']} | {r['reason']}")
    req_id = _prompt_int("Enter Request ID to process: ")
    print("1. Approve")
    print("2. Reject")
    act = prompt_choice("Selection: ")
    comment = prompt_text("Lecturer comment (optional): ") or None

    try:
        if act == "1":
            request_service.approve(req_id, lecturer_comment=comment)
            print("Approved.")
        elif act == "2":
            request_service.reject(req_id, lecturer_comment=comment)
            print("Rejected.")
        else:
            print("Invalid selection.")
    except Exception as e:
        print(f"Error: {e}")


def _ui_summarize(report_service: ReportService, class_repo: ClassRepo, lecturer_id: int) -> None:
    print("\n[SUMMARIZE ATTENDANCE]")
    classes = class_repo.list_by_filter(lecturer_id=lecturer_id)
    if not classes:
        print("You have no classes.")
        return
    for c in classes:
        print(f"- ClassID={c.class_id} | {c.class_code} | {c.class_name}")
    class_id = _prompt_int("Enter Class ID: ")
    date_from = prompt_text("From date (YYYY-MM-DD) or blank: ") or None
    date_to = prompt_text("To date (YYYY-MM-DD) or blank: ") or None

    try:
        rows = report_service.summarize(class_id, date_from=date_from, date_to=date_to)
        if not rows:
            print("No data.")
            return
        print("StudentID | Present | Late | Absent | Excused | Total")
        print("-" * 70)
        for r in rows:
            print(f"{r['student_id']} | {r['present']} | {r['late']} | {r['absent']} | {r['excused']} | {r['total']}")
    except Exception as e:
        print(f"Error: {e}")


def _ui_export(report_service: ReportService, class_repo: ClassRepo, lecturer_id: int) -> None:
    print("\n[EXPORT EXCEL REPORT]")
    classes = class_repo.list_by_filter(lecturer_id=lecturer_id)
    if not classes:
        print("You have no classes.")
        return
    for c in classes:
        print(f"- ClassID={c.class_id} | {c.class_code} | {c.class_name}")

    class_id = _prompt_int("Enter Class ID: ")
    date_from = prompt_text("From date (YYYY-MM-DD) or blank: ") or None
    date_to = prompt_text("To date (YYYY-MM-DD) or blank: ") or None
    output_path = prompt_text("Output folder OR full .xlsx path (default: reports): ").strip() or "reports"

    try:
        file_path = report_service.export_excel(class_id, output_path, date_from=date_from, date_to=date_to)
        print(f"Exported: {file_path}")
    except Exception as e:
        print(f"Error: {e}")
