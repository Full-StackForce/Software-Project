from pathlib import Path
import uvicorn
from fastapi import FastAPI
from sqlalchemy import inspect, text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import goal as goalRoute
from routers import auth
from routers import user as userRoute
from routers import workout as workoutRoute
from routers import challenge as challengeRoute
from routers import habit as habitRoute
from routers import dashboard as dashboardRoute
from routers import weight_log as weightLogRoute
from dependencies.config import conf
from dependencies.database import engine, Base
from models.model_loader import load_models


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goalRoute.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(userRoute.router, tags=["users"])
app.include_router(workoutRoute.router, tags=["workouts"])
app.include_router(habitRoute.router, tags=["habits"])
app.include_router(dashboardRoute.router, tags=["dashboard"])
app.include_router(weightLogRoute.router, tags=["weight-logs"])
app.include_router(challengeRoute.router, tags=["challenges"])
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


def ensure_user_profile_columns() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    statements = []

    if "gender" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN gender VARCHAR(30) NULL")
    if "height_cm" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN height_cm FLOAT NULL")
    if "weight_kg" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN weight_kg FLOAT NULL")
    if "target_weight_kg" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN target_weight_kg FLOAT NULL")

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))


load_models()
Base.metadata.create_all(bind=engine)
ensure_user_profile_columns()

@app.get("/login")
def login_page():
    return FileResponse(Path("frontend") / "login.html")


@app.get("/accounts")
@app.get("/signup/{step_name}")
def accounts_page(step_name: str | None = None):
    return FileResponse(Path("frontend") / "accounts.html")

@app.get("/")
@app.get("/index")
def index_page():
    return FileResponse(Path("frontend") / "index.html")

@app.get("/challanges")
def challenges_page():
    return FileResponse(Path("frontend") / "challanges.html")

@app.get("/dashboard")
def dashboard_page():
    return FileResponse(Path("frontend") / "dashboard.html")

@app.get("/home")
def home_page():
    return FileResponse(Path("frontend") / "home.html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

