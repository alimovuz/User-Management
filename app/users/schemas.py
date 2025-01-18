from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsersSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str