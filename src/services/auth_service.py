from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.repositories.user_repo import UserRepo, UserRow
from src.utils.security import verify_password
from src.utils.time_utils import now, minutes_from_now

LOCK_AFTER_FAILS = 5
LOCK_MINUTES = 10


@dataclass
class AuthResult:
    ok: bool
    message: str
    user: Optional[UserRow] = None


class AuthService:
    """Use case UC01: Login + lockout policy (5 fails)."""

    def __init__(self, user_repo: Optional[UserRepo] = None) -> None:
        self.user_repo = user_repo or UserRepo()

    def login(self, username: str, password: str) -> AuthResult:
        user = self.user_repo.get_by_username(username)
        if not user:
            return AuthResult(False, "Username or password is incorrect.")

        # If locked, refuse login until lock expires
        if user.locked_until:
            try:
                locked_until = datetime.fromisoformat(user.locked_until)
                if locked_until > now():
                    return AuthResult(False, f"Account is locked until {locked_until.isoformat(sep=' ', timespec='minutes')}.")
            except Exception:
                return AuthResult(False, "Account is locked. Please contact administrator.")

        # Verify password
        if not verify_password(password, user.password_hash):
            fails = user.failed_attempts + 1
            self.user_repo.update_failed_attempts(user.user_id, fails)

            if fails >= LOCK_AFTER_FAILS:
                locked_until = minutes_from_now(LOCK_MINUTES).isoformat()
                self.user_repo.set_lock(user.user_id, locked_until)
                return AuthResult(False, f"Too many failed attempts. Account locked for {LOCK_MINUTES} minutes.")

            return AuthResult(False, f"Username or password is incorrect. ({fails}/{LOCK_AFTER_FAILS})")

        # Success: reset fail/lock state
        self.user_repo.reset_login_state(user.user_id)
        user = self.user_repo.get_by_username(username)
        return AuthResult(True, "Login successful.", user=user)
