from fastapi import APIRouter, HTTPException
from typing import List

from controllers.goal_controller import create_goal, delete_goal, get_goal, list_goals, update_goal
from schemas.goal import GoalCreate, GoalResponse, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=GoalResponse)
def create_goal_route(payload: GoalCreate):
    return create_goal(payload)


@router.get("/", response_model=List[GoalResponse])
def get_goals():
    return list_goals()


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal_route(goal_id: int):
    goal = get_goal(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal_route(goal_id: int, payload: GoalUpdate):
    goal = update_goal(goal_id, payload)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/{goal_id}")
def delete_goal_route(goal_id: int):
    if not delete_goal(goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}
