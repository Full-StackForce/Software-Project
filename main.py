from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routers import index as indexRoute

from routers import index as indexRoute
from routers import goal as goalRoute
from routers import auth
from routers import user as userRoute
from dependencies.config import conf
from dependencies.database import engine, Base
import models.user


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

Base.metadata.create_all(bind=engine)

@app.get("/login")
def login_page():
    return FileResponse(Path("frontend") / "login.html")


@app.get("/accounts")
@app.get("/signup/{step_name}")
def accounts_page(step_name: str | None = None):
    return FileResponse(Path("frontend") / "accounts.html")

@app.get("/index")
def index_page():
    return FileResponse(Path("frontend") / "index.html")

@app.get("/challanges")
def challenges_page():
    return FileResponse(Path("frontend") / "challanges.html")

@app.get("/dashboard")
def dashboard_page():
    return FileResponse(Path("frontend") / "dashboard.html")

