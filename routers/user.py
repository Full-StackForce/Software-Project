from fastapi import APIRouter, HTTPException
from typing import List

from controllers.user_controller import create_user, list_users
from schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user_route(payload: UserCreate):
    return create_user(payload)


@router.get("/", response_model=List[UserResponse])
def get_users():
    return list_users()
