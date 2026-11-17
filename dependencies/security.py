import hashlib
import secrets
from datetime import UTC, datetime
from typing import Annotated

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from dependencies.database import get_db
from models.auth_session import AuthSession
from models.user import User


COOKIE_NAME = "pulsepoint_session"
SESSION_SECONDS = 60 * 60 * 24
password_hasher = PasswordHasher()
# Keep a failed lookup on the password verification path as well.
DUMMY_HASH = password_hasher.hash(secrets.token_urlsafe(32))


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(stored: str, password: str, scheme: str) -> bool:
    if scheme == "legacy_plaintext":
        return secrets.compare_digest(stored.encode(), password.encode())
    if scheme != "argon2id":
        return False
    try:
        return password_hasher.verify(stored, password)
    except (VerificationError, InvalidHashError):
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def require_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    session = db.get(AuthSession, token_digest(token)) if token else None
    if not session or session.expires_at <= datetime.now(UTC).replace(tzinfo=None):
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    return user


CurrentUser = Annotated[User, Depends(require_current_user)]


def require_same_user(user_id: int, user: User) -> None:
    if user_id != user.id:
        raise HTTPException(status_code=404, detail="Record not found")


def require_owned(record, user: User):
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
