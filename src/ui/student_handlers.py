from __future__ import annotations

<<<<<<< HEAD
from src.models.enums import RequestType
from src.services.attendance_service import AttendanceService
from src.services.request_service import RequestService, SubmitRequestInput
from src.repositories.warning_repo import WarningRepo
from src.ui.menus import show_student_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_yes_no


def run_student_dashboard(student_user) -> None:
    """
    Spec 8.5 Student Dashboard and Screens.
    """
    attendance = AttendanceService()
    requests = RequestService()
    warning_repo = WarningRepo()

    while True:
        warnings = warning_repo.list_by_filter(student_id=student_user.user_id)
        pending_reqs = requests.request_repo.list_by_filter(student_id=student_user.user_id, status="PENDING")

        print("\n[STUDENT DASHBOARD]")
        print(f"User: {student_user.full_name} (ID: {student_user.user_id})")
        print(f"Warnings: {len(warnings)} | Pending Requests: {len(pending_reqs)}")
        print("-" * 50)
        show_student_menu()
        print("-" * 50)

        c = prompt_choice("Selection: ")
        if c == "0":
            return
        elif c == "1":
            _ui_take_attendance(attendance, student_user.user_id)
        elif c == "2":
            _ui_view_attendance(attendance, student_user.user_id)
        elif c == "3":
            _ui_submit_request(requests, student_user.user_id)
        elif c == "4":
            _ui_view_warnings(warning_repo, student_user.user_id)
        else:
            print("Invalid menu selection. Please try again.")


def _ui_take_attendance(attendance: AttendanceService, student_id: int) -> None:
    print("\n[TAKE ATTENDANCE]")
    session_id_raw = prompt_text("Enter Session ID: ")
    try:
        session_id = int(session_id_raw)
    except ValueError:
        print("Invalid Session ID.")
        return

    pin = prompt_text("Enter PIN (if required): ")
    if pin == "":
        pin = None

    try:
        attendance.student_checkin(student_id, session_id, pin)
        print("Check-in successful.")
    except Exception as e:
        print(f"Error: {e}")


def _ui_view_attendance(attendance: AttendanceService, student_id: int) -> None:
    print("\n[VIEW ATTENDANCE ]")
    class_raw = prompt_text("Enter Course/Class ID (or leave blank to list all): ")
    class_id = int(class_raw) if class_raw.strip() else None
    date_from = prompt_text("Optional Date Range: From (YYYY-MM-DD): ") or None
    date_to = prompt_text("To (YYYY-MM-DD): ") or None
    print("-" * 50)

    try:
        rows = attendance.list_student_attendance(student_id=student_id, class_id=class_id, date_from=date_from, date_to=date_to)
        if not rows:
            print("No attendance records found.")
            return

        print("SessionID | Date       | Time  | Status   | Note")
        print("--------- | ---------- | ----- | -------- | ----")
        present = late = absent = 0
        for r in rows:
            status = r["status"]
            if status == "Present":
                present += 1
            elif status == "Late":
                late += 1
            elif status == "Absent":
                absent += 1
            note = r.get("note") or "-"
            print(f"{r['session_id']} | {r['session_date']} | {r['start_time']} | {status:<8} | {note}")

        print("-" * 50)
        print(f"Summary: Present={present}, Late={late}, Absent={absent}")
    except Exception as e:
        print(f"Error: {e}")


def _ui_submit_request(requests: RequestService, student_id: int) -> None:
    print("\n[SUBMIT REQUEST]")
    session_id_raw = prompt_text("Enter Session ID: ")
    try:
        session_id = int(session_id_raw)
    except ValueError:
        print("Invalid Session ID.")
        return

    print("Request Type: 1. Absent   2. Late")
    t = prompt_choice("Selection: ")
    if t == "1":
        req_type = RequestType.ABSENT
    elif t == "2":
        req_type = RequestType.LATE
    else:
        print("Invalid selection.")
        return

    reason = prompt_text("Reason (text): ")
    evidence = prompt_text("Optional Evidence File Path (leave blank if none): ") or None
    if not prompt_yes_no("Confirm submission (Y/N): "):
        print("Cancelled.")
        return

    try:
        rid = requests.submit_request(
            SubmitRequestInput(
                student_id=student_id,
                session_id=session_id,
                request_type=req_type,
                reason=reason,
                evidence_path=evidence,
            )
        )
        print(f"Submitted successfully. Request ID: {rid}")
    except Exception as e:
        print(f"Error: {e}")


def _ui_view_warnings(warning_repo: WarningRepo, student_id: int) -> None:
    print("\n[VIEW WARNINGS]")
    warns = warning_repo.list_by_filter(student_id=student_id)
    print("-" * 50)
    if not warns:
        print("No warnings.")
        return

    print("WarningID | Date       | Course/Class | Message")
    print("--------- | ---------- | ----------- | ------------------------------")
    for w in warns:
        print(f"{w.warning_id} | {w.created_at[:10]} | {w.class_id} | {w.message}")
=======
from typing import Optional

from src.services.attendance_service import AttendanceService
from src.services.request_service import RequestService, SubmitRequestInput
from src.models.enums import RequestType


class StudentHandlers:
    def __init__(self, student_id: int) -> None:
        self.student_id = student_id
        self.attendance_service = AttendanceService()
        self.request_service = RequestService()

    def show_menu(self) -> None:
        while True:
            print("\n====== STUDENT MENU ======")
            print("1. Check-in")
            print("2. View attendance")
            print("3. Submit absence / late request")
            print("4. View warnings")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.handle_checkin()
            elif choice == "2":
                self.handle_view_attendance()
            elif choice == "3":
                self.handle_submit_request()
            elif choice == "4":
                self.handle_view_warnings()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    # UC02
    def handle_checkin(self) -> None:
        try:
            session_id = int(input("Session ID: "))
            pin = input("PIN (leave blank if not required): ").strip()
            pin_input = pin if pin else None

            self.attendance_service.student_checkin(
                student_id=self.student_id,
                session_id=session_id,
                pin_input=pin_input,
            )
            print(" Check-in successful!")

        except Exception as e:
            print(f" Check-in failed: {e}")

    # UC03
    def handle_view_attendance(self) -> None:
        try:
            records = self.attendance_service.list_student_attendance(
                student_id=self.student_id
            )

            if not records:
                print("No attendance records found.")
                return

            print("\n--- Attendance Records ---")
            for r in records:
                print(
                    f"Session: {r['session_id']} | "
                    f"Status: {r['status']} | "
                    f"Time: {r['checkin_time']} | "
                    f"Note: {r['note']}"
                )

        except Exception as e:
            print(f" Error: {e}")

    # UC04
    def handle_submit_request(self) -> None:
        try:
            session_id = int(input("Session ID: "))
            print("Request type:")
            print("1. ABSENT")
            print("2. LATE")
            type_choice = input("Choose type: ").strip()

            if type_choice == "1":
                request_type = RequestType.ABSENT
            elif type_choice == "2":
                request_type = RequestType.LATE
            else:
                print("Invalid request type.")
                return

            reason = input("Reason: ").strip()
            evidence = input("Evidence path (optional): ").strip()
            evidence_path = evidence if evidence else None

            data = SubmitRequestInput(
                student_id=self.student_id,
                session_id=session_id,
                request_type=request_type,
                reason=reason,
                evidence_path=evidence_path,
            )

            request_id = self.request_service.submit_request(data)
            print(f" Request submitted successfully! (ID: {request_id})")

        except Exception as e:
            print(f" Submit request failed: {e}")

    # UC11
    def handle_view_warnings(self) -> None:
        try:
            warnings = self.attendance_service.list_warnings(
                student_id=self.student_id
            )

            if not warnings:
                print("🎉 No warnings. Good job!")
                return

            print("\n--- Attendance Warnings ---")
            for w in warnings:
                print(
                    f"Session: {w['session_id']} | "
                    f"Status: {w['status']} | "
                    f"Time: {w['checkin_time']} | "
                    f"Note: {w['note']}"
                )

        except Exception as e:
            print(f" Error: {e}")
>>>>>>> 884fd59bae424a002f06855426ec0cb61e41b294
