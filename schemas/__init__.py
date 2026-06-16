from .user import UserCreate, UserResponse
from .workout import WorkoutCreate, WorkoutResponse
from .habit import HabitCreate, HabitResponse, HabitUpdate
from .goal import GoalCreate, GoalResponse
from .dashboard import DashboardResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "WorkoutCreate",
    "WorkoutResponse",
    "HabitCreate",
    "HabitResponse",
    "HabitUpdate",
    "GoalCreate",
    "GoalResponse",
    "DashboardResponse",
]