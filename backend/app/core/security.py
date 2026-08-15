"""
Password hashing and JSON web tokens.

bcrypt is used directly rather than through passlib. passlib 1.7 is unmaintained
and its bcrypt backend breaks against bcrypt 4.x, which is the version everything
else installs. The direct API is small enough that the wrapper was not earning
its place.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# bcrypt hashes at most 72 bytes and silently ignores anything beyond that, which
# would make two long passwords sharing a 72-byte prefix interchangeable. Reject
# instead, so a password is never quietly weaker than the user believes.
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    encoded = password.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Password must be {MAX_PASSWORD_BYTES} bytes or fewer")
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    encoded = plain.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(encoded, hashed.encode("utf-8"))
    except ValueError:
        # A malformed hash in the database must not take the login route down.
        return False


def create_access_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expires}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """The claims, or None if the token is invalid, tampered with, or expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
