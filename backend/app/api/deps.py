"""
Shared dependencies: the database session, the current user, and role guards.

Access control matters more here than in a typical CRUD app. The survey promised
staff that results would be reported by department and never by person, and a
league table of departments visible to everyone changes how people answer the
next wave. So visibility is narrowed by role rather than left open.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.models import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error

    claims = decode_token(token)
    if not claims or not claims.get("sub"):
        raise credentials_error

    user = db.scalar(select(User).where(User.email == claims["sub"]))
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role):
    """
    Guard a route to particular roles.

    Returns 403 rather than 404 for an authenticated user without permission.
    Hiding the existence of an admin endpoint from a logged-in colleague buys
    nothing and makes support harder.
    """

    def guard(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role does not have access to this",
            )
        return user

    return guard


def visible_department_ids(user: User) -> Optional[set[int]]:
    """
    Which departments this user may see. None means all of them.

    A head of department sees only their own. If a HOD account has no department
    attached the answer is an empty set, not everything: an unconfigured account
    must fail closed.
    """
    if user.role in (Role.ADMIN, Role.LEADERSHIP):
        return None
    if user.role == Role.HOD:
        return {user.department_id} if user.department_id else set()
    return set()
