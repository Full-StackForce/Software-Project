from fastapi import APIRouter, HTTPException
from schemas.auth import LoginRequest, LoginResponse

router = APIRouter()

# TEMP USER (replace with DB later)
FAKE_USER = {
    "email": "test@example.com",
    "password": "password123"
}

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):

    if (
        credentials.email == FAKE_USER["email"]
        and credentials.password == FAKE_USER["password"]
    ):
        return LoginResponse(message="Login successful")

    raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )