from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt

from src.core.config import get_settings

settings = get_settings()

# API Key header for optional authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create a JWT token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm="HS256"
    )


def verify_token(token: str) -> dict:
    """Verify a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Validate API key if provided."""
    if api_key is None:
        return None
    
    # In a production environment, you would validate against a database
    # For now, we'll just check if it matches our secret key
    if api_key != settings.SECRET_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    return api_key
