from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import bearer_token, current_user_id
from app.core.config import get_settings
from app.schemas.customer import CustomerProfile, CustomerProfileUpdate
from app.services.supabase import SupabaseClient, SupabaseError

router = APIRouter(prefix="/customers/me", tags=["Customer profile"])


@router.get("", response_model=CustomerProfile)
async def get_my_profile(_: str = Depends(current_user_id), token: str = Depends(bearer_token)) -> CustomerProfile:
    try:
        profile = await SupabaseClient(get_settings()).profile(token)
        if profile is None:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        return CustomerProfile.model_validate(profile)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.put("", response_model=CustomerProfile)
async def update_my_profile(data: CustomerProfileUpdate, user_id: str = Depends(current_user_id), token: str = Depends(bearer_token)) -> CustomerProfile:
    try:
        profile = await SupabaseClient(get_settings()).upsert_profile(token, {"user_id": user_id, **data.model_dump()})
        return CustomerProfile.model_validate(profile)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

