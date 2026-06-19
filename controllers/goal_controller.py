from typing import List

from models.goal import Goal
from schemas.goal import GoalCreate

_goals: List[Goal] = []
_next_goal_id = 1


def create_goal(payload: GoalCreate) -> Goal:
    global _next_goal_id

    goal = Goal(
        id=_next_goal_id,
        user_id=payload.user_id,
        title=payload.title,
        description=payload.description,
        goal_type=payload.goal_type,
        target_value=payload.target_value,
        due_date=payload.due_date,
        completed=False,
    )

    _goals.append(goal)
    _next_goal_id += 1

    return goal


def list_goals() -> List[Goal]:
    return list(_goals)