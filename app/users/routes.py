from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from app.config.database import get_db
from app.users.schemas import UserCreateRequest, UserCreateResponse

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@user_router.post('/', response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateRequest, session: Session = Depends(get_db)):
    pass