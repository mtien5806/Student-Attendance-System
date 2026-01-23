from __future__ import annotations

from src.repositories.db import init_db
from src.services.auth_service import AuthService
from src.ui.menus import show_main_menu
from src.ui.prompts import prompt_choice, prompt_text, prompt_password
from src.models.enums import Role


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

        user = result.user
        role = user.role

        if role == Role.STUDENT.value:
            from src.ui.student_handlers import run_student_dashboard
            run_student_dashboard(user)

        elif role == Role.LECTURER.value:
            from src.ui.lecturer_handlers import run_lecturer_dashboard
            run_lecturer_dashboard(user)

        elif role == Role.ADMIN.value:
            from src.ui.admin_handlers import run_admin_dashboard
            run_admin_dashboard(admin_id=user.user_id, admin_name=user.full_name)

        else:
            print("Unknown role. Please contact administrator.")


if __name__ == "__main__":
    run()
