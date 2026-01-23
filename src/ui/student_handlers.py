from __future__ import annotations

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
