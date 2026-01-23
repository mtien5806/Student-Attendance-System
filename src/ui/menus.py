from __future__ import annotations


def show_main_menu() -> None:
    print("=" * 50)
    print("         STUDENT ATTENDANCE SYSTEM")
    print("=" * 50)
    print("1. Login")
    print("2. Exit")
    print("-" * 50)


def show_student_menu() -> None:
    print("1. Take Attendance (Check-in)")
    print("2. View Attendance")
    print("3. Submit Absence/Late Request")
    print("4. View Attendance Warnings")
    print("0. Logout")


def show_lecturer_menu() -> None:
    print("1. Create Attendance Session")
    print("2. Record Attendance")
    print("3. Approve/Reject Absence/Late Requests")
    print("4. Summarize Attendance")
    print("5. Export Attendance Report (Excel)")
    print("0. Logout")


def show_admin_menu() -> None:
    print("1. Search Attendance")
    print("2. Manage Attendance")
    print("0. Logout")
