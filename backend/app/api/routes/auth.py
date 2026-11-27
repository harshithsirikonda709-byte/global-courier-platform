from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.schemas.auth import AuthSession, ConfirmationPending, LoginRequest, RegisterRequest
from app.services.supabase import SupabaseClient, SupabaseError

router = APIRouter(prefix="/auth", tags=["Authentication"])


def session_from(payload: dict) -> AuthSession:
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")

    session_data = payload.get("session") if isinstance(payload.get("session"), dict) else payload
    user = payload.get("user") or (session_data.get("user") if isinstance(session_data, dict) else {}) or {}
    user_id = user.get("id") or payload.get("id") or (session_data.get("user_id") if isinstance(session_data, dict) else None)
    access_token = session_data.get("access_token") or payload.get("access_token")

    if not access_token or not user_id:
        raise ValueError("Invalid session payload from Supabase")

    refresh_token = session_data.get("refresh_token") or payload.get("refresh_token")
    expires_in = session_data.get("expires_in") or payload.get("expires_in")

    return AuthSession(
        access_token=str(access_token),
        refresh_token=str(refresh_token) if refresh_token else None,
        expires_in=int(expires_in) if expires_in is not None else None,
        user_id=str(user_id),
    )


@router.post(
    "/register",
    response_model=AuthSession,
    status_code=status.HTTP_201_CREATED,
    responses={
        202: {
            "model": ConfirmationPending,
            "description": "Registration successful, email confirmation pending",
        }
    },
)
async def register(data: RegisterRequest) -> AuthSession | Response:
    try:
        payload = await SupabaseClient(get_settings()).sign_up(
            data.email, data.password, {"full_name": data.full_name, "phone": data.phone}
        )
    except SupabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Unexpected response from authentication service")

    session_data = payload.get("session") if isinstance(payload.get("session"), dict) else payload
    access_token = session_data.get("access_token") if isinstance(session_data, dict) else None

    if not access_token:
        user_data = payload.get("user") if isinstance(payload.get("user"), dict) else payload
        user_id = user_data.get("id") if isinstance(user_data, dict) else None
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=ConfirmationPending(
                confirmation_required=True,
                message="Check your email to confirm registration before signing in.",
                user_id=str(user_id) if user_id else None,
                email=data.email,
            ).model_dump(exclude_none=True),
        )

    try:
        return session_from(payload)
    except (ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Malformed session payload received from authentication service")


@router.post("/login", response_model=AuthSession)
async def login(data: LoginRequest) -> AuthSession:
    try:
        payload = await SupabaseClient(get_settings()).sign_in(data.email, data.password)
    except SupabaseError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Unexpected response from authentication service")

    try:
        return session_from(payload)
    except (ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Malformed session payload received from authentication service")
