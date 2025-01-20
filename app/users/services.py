import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config.database import get_db
from app.config.security import get_password_hash, verify_password
from app.users.models import User, Token
from app.users.schemas import UserCreateRequest
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from jwt import PyJWTError

bearer_scheme = HTTPBearer()
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 30))
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

async def is_existing_user(db: Session, username: str, email: str) -> bool:
    db_user = db.query(User).filter_by(username=username).first()
    if db_user is None:
        return False
    db_user = db.query(User).filter_by(email=email).first()
    if db_user is None:
        return False
    return True

async def create_user(db: Session, data: UserCreateRequest):
    data.password = get_password_hash(data.password)
    new_user = User(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def authenticate_user(db: Session, data):
    db_user = db.query(User).filter_by(username=data.username).first()
    if db_user is None:
        return None
    if not verify_password(data.password, db_user.password):
        return None
    return db_user


async def save_token(user_id: int, token: str, jti: str, expires_in: int, db: Session):
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in)
    new_token = Token(user_id=user_id, token=token, expires_at=expires_at, jti=jti)
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("token_type")

        if user_id is None:
            raise credentials_exception

        if token_type != "access_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type not supported",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter_by(id=user_id).first()
        if user is None:
            raise credentials_exception

        return user
    except PyJWTError:
        raise credentials_exception