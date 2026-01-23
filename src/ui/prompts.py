from __future__ import annotations

import getpass


def prompt_choice(prompt: str = "Selection: ") -> str:
    return input(prompt).strip()


def prompt_text(label: str) -> str:
    return input(label).strip()


def prompt_password(label: str = "Password: ") -> str:
    """
    Masked input when possible.
    On some terminals (notably VS Code / some Windows shells), getpass may fail or not accept input.
    In that case we fall back to normal input().
    """
    try:
        return getpass.getpass(label)
    except (Exception, KeyboardInterrupt):
        # Fallback: visible input
        return input(label).strip()


def prompt_yes_no(label: str) -> bool:
    while True:
        v = input(label).strip().lower()
        if v in ("y", "yes"):
            return True
        if v in ("n", "no"):
            return False
        print("Please enter Y/N.")
