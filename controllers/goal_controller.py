from typing import List

from models.habit import Habit
from models.goal import Goal
from schemas.goal import GoalCreate, GoalUpdate

_goals: List[Goal] = []
_next_goal_id = 1


def _normalize_goal_type(goal_type: str) -> str:
    return goal_type.strip().lower().replace("-", " ").replace("_", " ")


def _evaluate_goal_completion(goal: Goal, habits: List[Habit]) -> bool:
    normalized_goal_type = _normalize_goal_type(goal.goal_type)

    if normalized_goal_type == "habit count":
        return len(habits) >= goal.target_value
    if normalized_goal_type in {"habit completed", "habit completion", "habit completed today"}:
        completed_habits = sum(1 for habit in habits if habit.completed_today)
        return completed_habits >= goal.target_value
    if normalized_goal_type == "habit streak":
        total_streak = sum(habit.streak_count for habit in habits)
        return total_streak >= goal.target_value

    return goal.completed


def refresh_goals_for_user(user_id: int, habits: List[Habit] | None = None) -> List[Goal]:
    if habits is None:
        from controllers.habit_controller import list_habits_by_user

        habits = list_habits_by_user(user_id)

    user_goals: List[Goal] = []
    for goal in _goals:
        if goal.user_id != user_id:
            continue
        goal.completed = _evaluate_goal_completion(goal, habits)
        user_goals.append(goal)

    return user_goals


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

    refresh_goals_for_user(payload.user_id)

    return goal


def list_goals() -> List[Goal]:
    return list(_goals)


def list_goals_by_user(user_id: int) -> List[Goal]:
    return [goal for goal in _goals if goal.user_id == user_id]


def get_goal(goal_id: int) -> Goal | None:
    return next((goal for goal in _goals if goal.id == goal_id), None)


def update_goal(goal_id: int, payload: GoalUpdate) -> Goal | None:
    goal = get_goal(goal_id)
    if not goal:
        return None

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(goal, field_name, value)

    refresh_goals_for_user(goal.user_id)
    return goal


def delete_goal(goal_id: int) -> bool:
    for index, goal in enumerate(_goals):
        if goal.id == goal_id:
            del _goals[index]
            return True
    return False
