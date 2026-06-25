from fastapi import APIRouter, HTTPException, Query
from typing import Any, List

from controllers.user_controller import create_user, delete_user, get_user, list_users, update_user
from schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user_route(payload: UserCreate):
    return create_user(payload)


@router.get("/", response_model=List[UserResponse])
def get_users():
    return list_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/details")
def get_user_details_route(user_id: int, fields: str | None = Query(default=None, description="Comma-separated user fields, for example: name,email")) -> dict[str, Any]:
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = {
        "id",
        "username",
        "name",
        "email",
        "timezone",
        "focus",
        "gender",
        "height_cm",
        "weight_kg",
        "target_weight_kg",
        "bedtime",
        "active_days",
        "hydration_goal",
        "created_at",
    }

    requested_fields = [field.strip() for field in fields.split(",")] if fields else ["id", "username", "name", "email"]
    invalid_fields = [field for field in requested_fields if field not in allowed_fields]
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields requested: {', '.join(invalid_fields)}",
        )

    return {field: getattr(user, field) for field in requested_fields}


@router.put("/{user_id}", response_model=UserResponse)
def update_user_route(user_id: int, payload: UserUpdate):
    user = update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user_route(user_id: int):
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
