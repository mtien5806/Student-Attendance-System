from __future__ import annotations

from src.repositories.db import init_db
from src.services.auth_service import AuthService
from src.ui.menus import show_main_menu, show_student_menu, show_lecturer_menu, show_admin_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_password
from src.models.enums import Role


def student_loop(user_id: int) -> None:
    """Student dashboard loop (skeleton)."""
    while True:
        show_student_menu()
        c = prompt_choice()
        if c == "0":
            return

        # TODO: map menu choices -> Student use cases
        # 1: Take Attendance (Check-in)
        # 2: View Attendance
        # 3: Submit Absence/Late Request
        # 4: View Attendance Warnings
        print("Student feature not implemented yet:", c)


def lecturer_loop(user_id: int) -> None:
    """Lecturer dashboard loop (skeleton)."""
    while True:
        show_lecturer_menu()
        c = prompt_choice()
        if c == "0":
            return

        # TODO: map menu choices -> Lecturer use cases
        # 1: Create Attendance Session
        # 2: Record Attendance
        # 3: Approve/Reject Requests
        # 4: Summarize Attendance
        # 5: Export Excel Report
        print("Lecturer feature not implemented yet:", c)


def admin_loop(user_id: int) -> None:
    """Administrator dashboard loop (skeleton)."""
    while True:
        show_admin_menu()
        c = prompt_choice()
        if c == "0":
            return

        # TODO: map menu choices -> Admin use cases
        # 1: Search Attendance
        # 2: Manage Attendance
        print("Admin feature not implemented yet:", c)


def run() -> None:
    """Entry point: init DB -> main menu -> login -> role dashboards."""
    init_db()
    auth = AuthService()

    while True:
        show_main_menu()
        c = prompt_choice()

        if c == "2":
            print("Goodbye.")
            return

        if c != "1":
            print("Invalid selection. Please try again.")
            continue

        print("\n[LOGIN]")
        username = prompt_text("Username: ")
        password = prompt_password("Password: ")

        result = auth.login(username, password)
        print(result.message)

        if not result.ok or result.user is None:
            continue

        role = result.user.role
        if role == Role.STUDENT.value:
            student_loop(result.user.user_id)
        elif role == Role.LECTURER.value:
            lecturer_loop(result.user.user_id)
        elif role == Role.ADMIN.value:
            admin_loop(result.user.user_id)
        else:
            print("Unknown role. Please contact administrator.")


if __name__ == "__main__":
    run()
