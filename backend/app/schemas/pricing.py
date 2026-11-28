from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.booking import ParcelCategory


class PackagingStatus(str, Enum):
    ORIGINAL = "ORIGINAL"
    REPACKAGED = "REPACKAGED"
    CUSTOM_CRATING = "CUSTOM_CRATING"
    DAMAGED = "DAMAGED"


class PricingCalculateRequest(BaseModel):
    weight_kg: float = Field(gt=0, le=1000, description="Package weight in kilograms")
    length_cm: float = Field(gt=0, le=500, description="Package length in cm")
    width_cm: float = Field(gt=0, le=500, description="Package width in cm")
    height_cm: float = Field(gt=0, le=500, description="Package height in cm")
    category: ParcelCategory = Field(default=ParcelCategory.GENERAL, description="Parcel content category")
    packaging_status: PackagingStatus | None = Field(default=None, description="Packaging condition status")
    pickup_state: str = Field(default="", description="Origin state for interstate routing")
    receiver_state: str = Field(default="", description="Destination state for interstate routing")


class PricingCalculateResponse(BaseModel):
    base_fee: float
    chargeable_weight_kg: float
    volumetric_weight_kg: float
    weight_fee: float
    category_surcharge: float
    packaging_surcharge: float
    interstate_fee: float
    subtotal: float
    tax_amount: float
    total_price: float
