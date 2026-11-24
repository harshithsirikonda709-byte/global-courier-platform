from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException, Request
from jwt import InvalidTokenError, PyJWKClient, decode
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError

from app.core.config import get_settings


@lru_cache
def project_keys(issuer: str) -> PyJWKClient:
    return PyJWKClient(f"{issuer}/.well-known/jwks.json", timeout=5)


def current_user_id(request: Request) -> str:
    token = bearer_token(request)
    settings = get_settings()
    issuer = settings.supabase_url.rstrip("/") + "/auth/v1"
    algorithm = settings.supabase_jwt_algorithm
    if not settings.supabase_url or (algorithm == "HS256" and not settings.supabase_jwt_secret):
        raise HTTPException(status_code=503, detail="JWT validation is not configured")
    try:
        key = settings.supabase_jwt_secret if algorithm == "HS256" else project_keys(issuer).get_signing_key_from_jwt(token).key
        claims = decode(token, key, algorithms=[algorithm], audience="authenticated", issuer=issuer,
                        options={"require": ["iss", "aud", "exp", "sub"]})
        return str(UUID(claims["sub"]))
    except PyJWKClientConnectionError:
        raise HTTPException(status_code=503, detail="Supabase signing keys are unavailable")
    except (InvalidTokenError, PyJWKClientError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


def bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    return auth[7:]
