from dependencies.security import CurrentUser, require_owned, require_same_user
from fastapi import APIRouter, HTTPException
from typing import List

from controllers.goal_controller import create_goal, delete_goal, get_goal, list_goals_by_user, update_goal
from schemas.goal import GoalCreate, GoalResponse, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=GoalResponse)
def create_goal_route(payload: GoalCreate, user: CurrentUser):
    payload = payload.model_copy(update={"user_id": user.id})
    return create_goal(payload)


@router.get("/", response_model=List[GoalResponse])
def get_goals(user: CurrentUser):
    return list_goals_by_user(user.id)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal_route(goal_id: int, user: CurrentUser):
    return require_owned(get_goal(goal_id), user)


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal_route(goal_id: int, payload: GoalUpdate, user: CurrentUser):
    require_owned(get_goal(goal_id), user)
    goal = update_goal(goal_id, payload)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/{goal_id}")
def delete_goal_route(goal_id: int, user: CurrentUser):
    require_owned(get_goal(goal_id), user)
    if not delete_goal(goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}
