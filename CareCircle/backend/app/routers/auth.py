from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..auth import get_current_user, provision_family_user
from ..config import get_settings
from ..database import get_db
from ..models import User
from ..schemas import (
    AuthResponse,
    ConfirmationPending,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from ..services.supabase import SupabaseClient, SupabaseError


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def session_from(payload: dict) -> AuthResponse:
    if not isinstance(payload, dict):
        raise ValueError("Supabase session payload must be an object")

    session_data = payload.get("session") if isinstance(payload.get("session"), dict) else payload
    user_data = payload.get("user") or (
        session_data.get("user") if isinstance(session_data, dict) else None
    )
    access_token = session_data.get("access_token") if isinstance(session_data, dict) else None
    user_id = user_data.get("id") if isinstance(user_data, dict) else None
    if not access_token or not user_id:
        raise ValueError("Supabase session is missing its access token or user")

    email = user_data.get("email")
    metadata = user_data.get("user_metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    if not email:
        raise ValueError("Supabase user profile is incomplete")
    full_name = metadata.get("full_name") or metadata.get("name") or str(email).split("@", 1)[0]

    refresh_token = session_data.get("refresh_token")
    expires_in = session_data.get("expires_in")
    return AuthResponse(
        access_token=str(access_token),
        refresh_token=str(refresh_token) if refresh_token else None,
        expires_in=int(expires_in) if expires_in is not None else None,
        user=UserResponse(
            id=str(user_id),
            full_name=str(full_name),
            email=str(email),
            phone=metadata.get("phone"),
            account_type=metadata.get("account_type", "family")
            if metadata.get("account_type") in ("family", "companion", "parent")
            else "family",
            is_admin=str(user_id) in get_settings().admin_user_ids,
        ),
    )


def save_platform_user(db: Session, user_data: dict, fallback_name: str | None = None) -> User:
    user_id = user_data.get("id")
    email = user_data.get("email")
    if not user_id or not email:
        raise ValueError("Supabase user profile is incomplete")
    try:
        user_id = str(UUID(str(user_id)))
    except ValueError as exc:
        raise ValueError("Supabase returned an invalid user ID") from exc

    metadata = user_data.get("user_metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    return provision_family_user(
        db,
        user_id=user_id,
        email=str(email),
        full_name=metadata.get("full_name") or metadata.get("name") or fallback_name,
        phone=metadata.get("phone"),
        account_type=metadata.get("account_type", "family")
        if metadata.get("account_type") in ("family", "companion", "parent")
        else "family",
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={202: {"model": ConfirmationPending}},
)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse | Response:
    try:
        result = await SupabaseClient(get_settings()).sign_up(
            str(payload.email),
            payload.password,
            {
                "full_name": payload.full_name,
                "phone": payload.phone,
                "account_type": payload.account_type,
            },
        )
    except SupabaseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not isinstance(result, dict):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unexpected response from authentication service")

    user_data = result.get("user") if isinstance(result.get("user"), dict) else result
    try:
        local_user = save_platform_user(db, user_data, payload.full_name)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Malformed user profile received from authentication service")

    session_data = result.get("session") if isinstance(result.get("session"), dict) else result
    if not session_data.get("access_token"):
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=ConfirmationPending(
                message="Check your email to confirm registration before signing in.",
                user_id=local_user.id,
                email=local_user.email,
            ).model_dump(mode="json", exclude_none=True),
        )

    try:
        return session_from(result)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Malformed session payload received from authentication service")


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        result = await SupabaseClient(get_settings()).sign_in(str(payload.email), payload.password)
    except SupabaseError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if not isinstance(result, dict):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unexpected response from authentication service")

    try:
        session = session_from(result)
        user_data = result.get("user")
        if not isinstance(user_data, dict):
            raise ValueError("Supabase session is missing its user")
        local_user = save_platform_user(db, user_data, session.user.full_name)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Malformed session payload received from authentication service")

    session.user = UserResponse.model_validate(local_user)
    session.user.is_admin = local_user.id in get_settings().admin_user_ids
    return session


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    response = UserResponse.model_validate(current_user)
    response.is_admin = current_user.id in get_settings().admin_user_ids
    return response
