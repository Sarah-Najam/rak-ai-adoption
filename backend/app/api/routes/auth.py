"""Login and the current user."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password
from app.models.models import User
from app.schemas.schemas import LoginRequest, Token, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: DbSession) -> Token:
    user = db.scalar(select(User).where(User.email == payload.email))

    # The same message whether the email is unknown or the password is wrong.
    # Distinguishing them turns the login form into an account enumeration tool.
    if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return Token(access_token=create_access_token(user.email, {"role": user.role.value}))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user
