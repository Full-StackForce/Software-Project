from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: int
    name: str
    email: str
    current_streak: int


class CurrentUserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    current_streak: int