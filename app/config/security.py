import secrets
from datetime import timedelta, datetime, timezone
import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
import os

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 30))
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int):
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "token_type": "access_token",
        "user_id": user_id,
        "exp": expires,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int, jti: str):
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "token_type": "refresh_token",
        "user_id": user_id,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
        'jti': jti
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_jti():
    return secrets.token_hex()