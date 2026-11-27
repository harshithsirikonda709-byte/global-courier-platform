from functools import lru_cache
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import CompanionProfile, Family, FamilyMember, User


bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def project_keys(issuer: str) -> PyJWKClient:
    return PyJWKClient(f"{issuer}/.well-known/jwks.json", timeout=5)


def provision_family_user(
    db: Session,
    user_id: str,
    email: str,
    full_name: str | None = None,
    phone: str | None = None,
    account_type: str = "family",
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        name = (full_name or "").strip() or email.split("@", 1)[0]
        user = User(
            id=user_id,
            email=email,
            phone=phone,
            full_name=name,
            account_type=account_type,
            account_status="active",
        )
        db.add(user)
        db.flush()
    elif user.account_status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive")

    if user.account_type == "family":
        membership = db.query(FamilyMember).filter(
            FamilyMember.user_id == user.id,
            FamilyMember.status == "active",
        ).first()
        if membership is None:
            family = Family(
                primary_user_id=user.id,
                name=f"{user.full_name} Family",
                account_status="active",
            )
            db.add(family)
            db.flush()
            db.add(FamilyMember(
                family_id=family.id,
                user_id=user.id,
                role="owner",
                status="active",
            ))
    elif user.account_type == "companion":
        if db.query(CompanionProfile).filter(CompanionProfile.user_id == user.id).first() is None:
            db.add(CompanionProfile(
                user_id=user.id,
                display_name=user.full_name,
                bio="",
                languages=[],
                service_area="",
                identity_document_type="",
                identity_status="pending",
                approval_status="pending",
            ))
    elif user.account_type != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account type")

    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")

    settings = get_settings()
    if not settings.supabase_url:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT validation is not configured")

    issuer = settings.supabase_url.rstrip("/") + "/auth/v1"
    try:
        header = jwt.get_unverified_header(credentials.credentials)
        token_algorithm = header.get("alg")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

    if settings.supabase_jwt_algorithm == "AUTO":
        allowed_algorithms = ["HS256", "ES256", "RS256"]
    else:
        allowed_algorithms = [settings.supabase_jwt_algorithm]
    if token_algorithm not in allowed_algorithms:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

    if token_algorithm == "HS256":
        if not settings.supabase_jwt_secret:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT validation is not configured")
        key = settings.supabase_jwt_secret
    elif token_algorithm in ("ES256", "RS256"):
        try:
            key = project_keys(issuer).get_signing_key_from_jwt(credentials.credentials).key
        except PyJWKClientConnectionError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Supabase signing keys are unavailable")
        except (PyJWKClientError, InvalidTokenError, KeyError, ValueError, AttributeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

    try:
        claims = jwt.decode(
            credentials.credentials,
            key,
            algorithms=[token_algorithm],
            audience="authenticated",
            issuer=issuer,
            options={"require": ["iss", "aud", "exp", "sub"]},
        )
        user_id = str(UUID(claims["sub"]))
    except (InvalidTokenError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

    email = claims.get("email")
    if not isinstance(email, str) or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User email is missing from access token")
    metadata = claims.get("user_metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    full_name = metadata.get("full_name") or metadata.get("name")
    phone = metadata.get("phone")
    account_type = metadata.get("account_type")
    if account_type not in ("family", "companion", "parent"):
        account_type = "family"
    return provision_family_user(
        db,
        user_id=user_id,
        email=email,
        full_name=full_name if isinstance(full_name, str) else None,
        phone=phone if isinstance(phone, str) else None,
        account_type=account_type,
    )


def require_family_member(db: Session, user: User) -> FamilyMember:
    if user.account_type != "family":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A family account is required")
    membership = db.query(FamilyMember).filter(
        FamilyMember.user_id == user.id,
        FamilyMember.status == "active",
    ).first()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A family membership is required",
        )
    return membership


def require_companion(user: User) -> User:
    if user.account_type != "companion":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A companion account is required")
    return user


def require_admin(user: User) -> User:
    if user.id not in get_settings().admin_user_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access is required")
    return user
