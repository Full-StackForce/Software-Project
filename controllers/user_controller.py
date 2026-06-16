from datetime import datetime
from typing import List

from models.user import User
from schemas.user import UserCreate

_users: List[User] = []
_next_user_id = 1


def create_user(payload: UserCreate) -> User:
    global _next_user_id
    user = User(
        id=_next_user_id,
        username=payload.username,
        email=payload.email,
        created_at=datetime.utcnow(),
    )
    _users.append(user)
    _next_user_id += 1
    return user


def list_users() -> List[User]:
    return list(_users)
