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
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class SingleUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str