from fastapi import HTTPException, Request, status
from jwt import InvalidTokenError, decode

from app.core.config import get_settings


def current_user_id(request: Request) -> str:
    """Validate a Supabase access token and return its authenticated user UUID."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    secret = get_settings().supabase_jwt_secret
    if not secret:
        raise HTTPException(status_code=503, detail="JWT validation is not configured")
    try:
        claims = decode(auth[7:], secret, algorithms=["HS256"], audience="authenticated")
        return str(claims["sub"])
    except (InvalidTokenError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


def bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    return auth[7:]

