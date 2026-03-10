"""
Authentication utilities for Semantic Vision
JWT tokens for guardians/teachers/admin, PIN for students
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Security configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "leximaster-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for JWT tokens
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    Returns user dict with id, email, role
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role")
    }


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_guardian(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require guardian role"""
    if current_user.get("role") not in ["guardian", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guardian access required"
        )
    return current_user


async def get_current_teacher(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require teacher role"""
    if current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user


async def get_current_brand_partner(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require brand_partner role"""
    if current_user.get("role") not in ["brand_partner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brand partner access required"
        )
    return current_user
