from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass

_ALGO = "sha256"
_ITERATIONS = 120_000
_SALT_BYTES = 16
_KEY_BYTES = 32


@dataclass(frozen=True)
class PasswordHash:
    """Stored format: pbkdf2_sha256$iterations$salt_b64$dk_b64"""
    value: str


def hash_password(plain: str) -> PasswordHash:
    if plain is None:
        raise ValueError("Password is required")
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(_ALGO, plain.encode("utf-8"), salt, _ITERATIONS, dklen=_KEY_BYTES)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    dk_b64 = base64.b64encode(dk).decode("ascii")
    stored = f"pbkdf2_{_ALGO}${_ITERATIONS}${salt_b64}${dk_b64}"
    return PasswordHash(stored)


def verify_password(plain: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        if len(parts) != 4:
            return False
        algo_tag, iterations_s, salt_b64, dk_b64 = parts
        if not algo_tag.startswith("pbkdf2_"):
            return False
        algo = algo_tag.replace("pbkdf2_", "")
        iterations = int(iterations_s)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(dk_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(algo, plain.encode("utf-8"), salt, iterations, dklen=len(expected))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False
