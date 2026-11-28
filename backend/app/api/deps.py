from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, Request
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


async def current_user_claims(request: Request) -> dict:
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
        UUID(claims["sub"])
        return claims
    except (InvalidTokenError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


async def current_user_id(claims: dict = Depends(current_user_claims)) -> str:
    return str(claims["sub"])


def get_user_role(claims: dict, request: Request) -> str:
    dev_role = request.headers.get("X-User-Role")
    if dev_role:
        return dev_role.lower()

    if claims.get("role") in ("admin", "service_role"):
        return "admin"
    if claims.get("app_metadata", {}).get("role"):
        return str(claims["app_metadata"]["role"]).lower()
    if claims.get("user_metadata", {}).get("role"):
        return str(claims["user_metadata"]["role"]).lower()
    return "customer"


async def require_admin(request: Request, claims: dict = Depends(current_user_claims)) -> dict:
    role = get_user_role(claims, request)
    if role not in ("admin", "service_role"):
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    return claims


async def require_driver(request: Request, claims: dict = Depends(current_user_claims)) -> dict:
    role = get_user_role(claims, request)
    if role not in ("driver", "pickup_executive", "admin", "service_role"):
        raise HTTPException(status_code=403, detail="Forbidden: Pickup executive access required")
    return claims
