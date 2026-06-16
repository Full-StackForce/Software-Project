from fastapi import APIRouter
from typing import List

from controllers.goal_controller import create_goal, list_goals
from schemas.goal import GoalCreate, GoalResponse

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=GoalResponse)
def create_goal_route(payload: GoalCreate):
    return create_goal(payload)


@router.get("/", response_model=List[GoalResponse])
def get_goals():
    return list_goals()
