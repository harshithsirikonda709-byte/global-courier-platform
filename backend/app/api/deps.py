from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException, Request
import jwt
from jwt import InvalidTokenError, PyJWKClient, decode
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError

from app.core.config import get_settings


@lru_cache
def project_keys(issuer: str) -> PyJWKClient:
    return PyJWKClient(f"{issuer}/.well-known/jwks.json", timeout=5)


async def bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    token = auth[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token required")
    return token


async def current_user_id(request: Request) -> str:
    token = await bearer_token(request)
    settings = get_settings()

    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="JWT validation is not configured")

    issuer = settings.supabase_url.rstrip("/") + "/auth/v1"
    configured_algorithm = settings.supabase_jwt_algorithm

    try:
        header = jwt.get_unverified_header(token)
        token_alg = header.get("alg")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    if not token_alg:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    # Determine allowed algorithms
    if configured_algorithm == "AUTO":
        allowed_algorithms = ["HS256", "ES256", "RS256"]
    else:
        allowed_algorithms = [configured_algorithm]

    if token_alg not in allowed_algorithms:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    if token_alg == "HS256":
        if not settings.supabase_jwt_secret:
            raise HTTPException(status_code=503, detail="JWT validation is not configured")
        key = settings.supabase_jwt_secret
    elif token_alg in ("ES256", "RS256"):
        try:
            key = project_keys(issuer).get_signing_key_from_jwt(token).key
        except PyJWKClientConnectionError:
            raise HTTPException(status_code=503, detail="Supabase signing keys are unavailable")
        except (PyJWKClientError, InvalidTokenError, KeyError, ValueError, AttributeError):
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    try:
        claims = decode(
            token,
            key,
            algorithms=[token_alg],
            audience="authenticated",
            issuer=issuer,
            options={"require": ["iss", "aud", "exp", "sub"]},
        )
        return str(UUID(claims["sub"]))
    except (InvalidTokenError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
