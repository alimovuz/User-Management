from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from dotenv import load_dotenv
from app.config.database import get_db
from app.config.security import create_access_token, generate_jti, create_refresh_token
from app.users.models import User
from app.users.schemas import UserCreateRequest, UserCreateResponse, LoginRequest, LoginResponse, UsersSchema, \
    SingleUserSchema
from app.users.services import is_existing_user, create_user, authenticate_user, save_token, get_current_user
import os

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

load_dotenv()
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


@user_router.post('', response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreateRequest, session: Session = Depends(get_db)):
    db_user = await is_existing_user(db=session, username=user.username, email=str(user.email))
    if db_user:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Username or email already exists")

    new_user = await create_user(db=session, data=user)
    return new_user


@user_router.post('/login', response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(data: LoginRequest, session: Session = Depends(get_db)):
    user = await authenticate_user(data=data, db=session)

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password! Please try again."
        )

    access_token = create_access_token(user.id)
    jti = generate_jti()
    refresh_token = create_refresh_token(user.id, jti=jti)

    await save_token(
        user_id=user.id,
        token=refresh_token,
        jti=jti,
        expires_in=REFRESH_TOKEN_EXPIRE_DAYS,
        db=session
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@user_router.get('', response_model=List[UsersSchema])
async def get_users(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = session.query(User).all()
    return users


@user_router.get('/{user_id}', response_model=SingleUserSchema)
async def get_single_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

@user_router.put('/{user_id}', response_model=UserCreateResponse)
async def update_user(user_id, data: UserCreateRequest, session: Session = Depends(get_db)):
    db_user = session.query(User).filter_by(id=user_id).first()
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.username = data.username
    db_user.email = data.email
    db_user.first_name = data.first_name
    db_user.last_name = data.last_name

    session.commit()
    session.refresh(db_user)
    return db_user
