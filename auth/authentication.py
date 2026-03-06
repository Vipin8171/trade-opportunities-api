"""
JWT Authentication module.
Provides simple username/password auth with JWT tokens.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.schemas import TokenData
from utils.logger import logger

# ─── Security Scheme ────────────────────────────────────────────────────────────
security = HTTPBearer()

# ─── In-Memory User Store ────────────────────────────────────────────────────────
# Simple demo users (in production, use hashed passwords + database)
DEMO_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "analyst": {"password": "analyst123", "role": "user"},
    "guest": {"password": "guest123", "role": "guest"},
}


def verify_user(username: str, password: str) -> Optional[dict]:
    """Verify username and password against in-memory store."""
    user = DEMO_USERS.get(username)
    if user and user["password"] == password:
        logger.info(f"User '{username}' authenticated successfully")
        return {"username": username, "role": user["role"]}
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Token created for user: {data.get('sub', 'unknown')}")
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Dependency: extracts and validates the current user from the JWT token.
    Raises 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception
