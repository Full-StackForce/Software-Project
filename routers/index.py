from fastapi import FastAPI

from routers import user as user_router
from routers import workout as workout_router
from routers import habit as habit_router
from routers import goal as goal_router
from routers import dashboard as dashboard_router


def load_routes(app: FastAPI) -> None:
    app.include_router(user_router.router)
    app.include_router(workout_router.router)
    app.include_router(habit_router.router)
    app.include_router(goal_router.router)
    app.include_router(dashboard_router.router)

    @app.get("/")
    def read_root() -> dict:
        return {"message": "PulsePoint API is up"}
