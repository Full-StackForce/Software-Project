from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import FileResponse, JSONResponse
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
from dependencies.migrations import ensure_auth_columns
from models.model_loader import load_models


app = FastAPI()


@app.middleware("http")
async def protect_browser_requests(request: Request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin")
        expected_origin = str(request.base_url).rstrip("/")
        if (origin and origin != expected_origin) or request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse(status_code=403, content={"detail": "Cross-origin changes are not allowed."})
        if request.headers.get("x-pulsepoint-request") != "1":
            return JSONResponse(status_code=403, content={"detail": "Missing request protection header."})
    response = await call_next(request)
    if not request.url.path.startswith("/frontend/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def safe_validation_error(request: Request, exc: RequestValidationError):
    # Pydantic's input/context may include passwords or the entire request body.
    errors = [{key: error[key] for key in ("loc", "msg", "type")} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})

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


def initialize_database_schema() -> None:
    load_models()
    try:
        Base.metadata.create_all(bind=engine)
        ensure_user_profile_columns()
        ensure_auth_columns(engine)
    except SQLAlchemyError as exc:
        # Keep the app bootable when DB is temporarily unavailable.
        print("Warning: database initialization skipped; check local database availability and schema.")


initialize_database_schema()

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

@app.get("/challenges")
def challenges_page():
    return FileResponse(Path("frontend") / "challenges.html")

@app.get("/dashboard")
def dashboard_page():
    return FileResponse(Path("frontend") / "dashboard.html")

@app.get("/home")
def home_page():
    return FileResponse(Path("frontend") / "home.html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

