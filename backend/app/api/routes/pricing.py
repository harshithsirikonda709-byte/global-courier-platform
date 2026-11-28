from fastapi import APIRouter

from app.schemas.pricing import PricingCalculateRequest, PricingCalculateResponse
from app.services.pricing import calculate_pricing

router = APIRouter(prefix="/pricing", tags=["Pricing Engine"])


@router.post("/calculate", response_model=PricingCalculateResponse)
async def calculate_shipping_price(payload: PricingCalculateRequest) -> PricingCalculateResponse:
    """Calculate transparent, real-time shipping price estimate.

    Includes chargeable weight computation (dead weight vs volumetric weight),
    base fee, category surcharges, packaging surcharges, and GST.
    """
    breakdown = calculate_pricing(
        weight_kg=payload.weight_kg,
        length_cm=payload.length_cm,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        category=payload.category,
        packaging_status=payload.packaging_status.value if payload.packaging_status else None,
        pickup_state=payload.pickup_state,
        receiver_state=payload.receiver_state,
    )
    return PricingCalculateResponse(**breakdown.to_dict())
