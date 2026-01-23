from __future__ import annotations

from src.models.enums import AttendanceStatus
from src.services.session_service import SessionService, CreateSessionInput
from src.services.attendance_service import AttendanceService
from src.services.request_service import RequestService
from src.services.report_service import ReportService
from src.repositories.class_repo import ClassRepo
from src.ui.menus import show_lecturer_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_yes_no


def _prompt_int(label: str, *, allow_zero: bool = False) -> int:
    while True:
        raw = prompt_text(label)
        try:
            v = int(raw)
            if v == 0 and not allow_zero:
                print("Value must be > 0.")
                continue
            return v
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


def run_lecturer_dashboard(lecturer_user) -> None:
    """
    Spec 8.6 Lecturer Dashboard and Screens.
    """
    session_service = SessionService()
    attendance_service = AttendanceService()
    request_service = RequestService()
    report_service = ReportService()
    class_repo = ClassRepo()

    while True:
        pending = request_service.list_requests_for_lecturer(lecturer_user.user_id, pending_only=True)
        print("\n[LECTURER DASHBOARD]")
        print(f"User: {lecturer_user.full_name} (ID: {lecturer_user.user_id})")
        print(f"Pending Requests: {len(pending)}")
        print("-" * 50)
        show_lecturer_menu()
        print("-" * 50)

        c = prompt_choice("Selection: ")
        if c == "0":
            return
        elif c == "1":
            _ui_create_session(session_service, class_repo, lecturer_user.user_id)
        elif c == "2":
            _ui_record_attendance(attendance_service, session_service)
        elif c == "3":
            _ui_process_requests(request_service, lecturer_user.user_id)
        elif c == "4":
            _ui_summarize(report_service)
        elif c == "5":
            _ui_export(report_service)
        else:
            print("Invalid menu selection. Please try again.")


def _ui_create_session(session_service: SessionService, class_repo: ClassRepo, lecturer_id: int) -> None:
    print("\n[CREATE SESSION]")
    class_id = _prompt_int("Enter Course/Class ID: ")
    session_date = prompt_text("Session Date (YYYY-MM-DD): ")
    start_time = prompt_text("Start Time (HH:MM): ")
    duration = _prompt_int("Duration (minutes): ")
    pin_enabled = prompt_yes_no("Require PIN? (Y/N): ")
    pin_code = None
    if pin_enabled:
        pin_code = prompt_text("If Yes, enter PIN (4–6 digits) or leave blank to auto-generate: ") or None

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
        session = session_service.session_repo.get_by_id(sid)
        print("-" * 50)
        print("Session created successfully.")
        print(f"Session ID: {sid}")
        if int(session.pin_enabled) == 1:
            print(f"PIN (if enabled): {session.pin_code}")
        print(f"Status: {session.status}")
    except Exception as e:
        print(f"Error: {e}")


def _ui_record_attendance(attendance_service: AttendanceService, session_service: SessionService) -> None:
    print("\n[RECORD  ATTENDANCE]")
    session_id = _prompt_int("Enter Session ID: ")

    try:
        # Print roster table immediately (spec)
        roster = attendance_service.get_roster_for_session(session_id)
        print("-" * 50)
        print("StudentID | StudentName | Current Status")
        print("--------- | ----------- | --------------")
        for r in roster:
            print(f"{r['student_id']} | {r['student_name']} | {r['status']}")
        print("-" * 50)

        while True:
            print("Actions:")
            print("1. Update a student status")
            print("2. Mark all as Present (batch)")
            print("3. Close session")
            print("0. Back")
            sel = prompt_choice("Selection: ")

            if sel == "0":
                return

            if sel == "1":
                student_id = _prompt_int("Enter StudentID: ")
                status = _prompt_status()
                note = prompt_text("Optional Note: ") or None
                if not prompt_yes_no("Confirm (Y/N): "):
                    print("Cancelled.")
                    continue
                attendance_service.update_status(session_id, student_id, status, note=note)
                print("Updated.")
                continue

            if sel == "2":
                if not prompt_yes_no("Confirm (Y/N): "):
                    print("Cancelled.")
                    continue
                attendance_service.mark_all_present(session_id)
                print("Done.")
                continue

            if sel == "3":
                if not prompt_yes_no("Confirm (Y/N): "):
                    print("Cancelled.")
                    continue
                session_service.close_session(session_id)
                print("Session closed.")
                continue

            print("Invalid menu selection. Please try again.")
    except Exception as e:
        print(f"Error: {e}")


def _ui_process_requests(request_service: RequestService, lecturer_id: int) -> None:
    print("\n[PROCESS REQUESTS]")
    print("Filter: 1. Pending only  2. All")
    f = prompt_choice("Selection: ")
    pending_only = (f != "2")

    requests = request_service.list_requests_for_lecturer(lecturer_id, pending_only=pending_only)
    print("-" * 50)
    if not requests:
        print("No requests found.")
        return

    print("RequestID | StudentID | SessionID | Type  | Reason (short) | Status")
    print("--------- | --------- | --------- | ----- | -------------- | ------")
    for r in requests:
        reason = (r["reason"][:12] + "...") if len(r["reason"]) > 15 else r["reason"]
        print(f"{r['request_id']} | {r['student_id']} | {r['session_id']} | {r['request_type']} | {reason} | {r['status']}")

    rid = _prompt_int("Enter RequestID to process (or 0 to back): ", allow_zero=True)
    if rid == 0:
        return

    print("Action: 1. Approve  2. Reject")
    act = prompt_choice("Selection: ")
    comment = prompt_text("Lecturer Comment (optional): ") or None
    if not prompt_yes_no("Confirm (Y/N): "):
        print("Cancelled.")
        return

    try:
        if act == "1":
            request_service.approve(rid, lecturer_comment=comment)
            print("Approved.")
        elif act == "2":
            request_service.reject(rid, lecturer_comment=comment)
            print("Rejected.")
        else:
            print("Invalid action.")
    except Exception as e:
        print(f"Error: {e}")


def _ui_summarize(report_service: ReportService) -> None:
    print("\n[SUMMARIZE ATTENDANCE]")
    class_id = _prompt_int("Enter Course/Class ID: ")
    date_from = prompt_text("Optional Date Range: From (YYYY-MM-DD): ") or None
    date_to = prompt_text("To (YYYY-MM-DD): ") or None
    print("-" * 50)

    try:
        rows = report_service.summarize(class_id, date_from=date_from, date_to=date_to)
        if not rows:
            print("No data.")
            return
        print("StudentID | Present | Late | Absent | Attendance Rate")
        print("--------- | ------- | ---- | ------ | ---------------")
        for r in rows:
            print(f"{r['student_id']} | {r['present']:>7} | {r['late']:>4} | {r['absent']:>6} | {r['attendance_rate']}%")
    except Exception as e:
        print(f"Error: {e}")


def _ui_export(report_service: ReportService) -> None:
    print("\n[EXPORT REPORT]")
    class_id = _prompt_int("Enter Course/Class ID: ")
    date_from = prompt_text("Optional Date Range: From (YYYY-MM-DD): ") or None
    date_to = prompt_text("To (YYYY-MM-DD): ") or None
    output_file = prompt_text("Enter output file path (e.g., reports/CSE101_Attendance.xlsx): ")
    if not output_file:
        output_file = "reports/report.xlsx"

    if not prompt_yes_no("Confirm export (Y/N): "):
        print("Cancelled.")
        return

    try:
        path = report_service.export_excel(class_id, output_file, date_from=date_from, date_to=date_to)
        print("Export completed successfully.")
        print(f"Saved to: {path}")
    except Exception as e:
        print(f"Error: {e}")
