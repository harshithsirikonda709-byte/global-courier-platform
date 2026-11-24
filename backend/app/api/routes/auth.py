from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.schemas.auth import AuthSession, LoginRequest, RegisterRequest
from app.services.supabase import SupabaseClient, SupabaseError

router = APIRouter(prefix="/auth", tags=["Authentication"])


def session_from(payload: dict) -> AuthSession:
    user = payload.get("user") or {}
    return AuthSession(
        access_token=payload["access_token"], refresh_token=payload.get("refresh_token"),
        expires_in=payload.get("expires_in"), user_id=user["id"],
    )


@router.post("/register", response_model=AuthSession, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest) -> AuthSession:
    try:
        payload = await SupabaseClient(get_settings()).sign_up(data.email, data.password, {"full_name": data.full_name, "phone": data.phone})
        if not payload.get("access_token"):
            raise HTTPException(status_code=202, detail="Registration created. Confirm your email before signing in.")
        return session_from(payload)
    except SupabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login", response_model=AuthSession)
async def login(data: LoginRequest) -> AuthSession:
    try:
        return session_from(await SupabaseClient(get_settings()).sign_in(data.email, data.password))
    except SupabaseError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

