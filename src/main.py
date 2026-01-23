from __future__ import annotations

from src.repositories.db import init_db
from src.services.auth_service import AuthService
from src.ui.menus import show_main_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_password
from src.models.enums import Role
from src.ui.student_handlers import run_student_dashboard
from src.ui.lecturer_handlers import run_lecturer_dashboard
from src.ui.admin_handlers import AdminHandlers


def run() -> None:
    """Entry point: init DB -> main menu -> login -> role dashboards."""
    init_db()
    auth = AuthService()
    admin_handlers = AdminHandlers()

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
            run_student_dashboard(result.user)
        elif role == Role.LECTURER.value:
            run_lecturer_dashboard(result.user)
        elif role == Role.ADMIN.value:
            admin_handlers.admin_menu()
        else:
            print("Unknown role. Please contact administrator.")


if __name__ == "__main__":
    run()
