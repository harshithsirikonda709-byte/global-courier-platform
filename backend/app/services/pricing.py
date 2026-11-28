"""Pricing Calculation Engine for Global Courier Platform.

Computes estimated and final pricing based on:
- Chargeable weight: max(dead weight, volumetric weight) where volumetric = (L*W*H)/5000
- Base service fee
- Category handling surcharges (fragile, electronics, perishable)
- Packaging surcharges (repackaging, custom crating)
- Interstate routing surcharges
- Standard logistics taxation (18% GST)
"""

from dataclasses import dataclass
from typing import Any

from app.schemas.booking import ParcelCategory


# Surcharge configurations (in INR)
BASE_FEE = 50.00
BASE_WEIGHT_THRESHOLD_KG = 0.5
RATE_PER_EXTRA_KG = 40.00
VOLUMETRIC_DIVISOR = 5000.0
INTERSTATE_SURCHARGE = 80.00
TAX_RATE_GST = 0.18

CATEGORY_SURCHARGES: dict[ParcelCategory, float] = {
    ParcelCategory.DOCUMENT: 0.00,
    ParcelCategory.CLOTHING: 20.00,
    ParcelCategory.GENERAL: 0.00,
    ParcelCategory.ELECTRONICS: 100.00,
    ParcelCategory.PERISHABLE: 120.00,
    ParcelCategory.FRAGILE: 150.00,
}

PACKAGING_SURCHARGES: dict[str, float] = {
    "ORIGINAL": 0.00,
    "REPACKAGED": 50.00,
    "CUSTOM_CRATING": 200.00,
    "DAMAGED": 0.00,
}


@dataclass
class PricingBreakdown:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_fee": self.base_fee,
            "chargeable_weight_kg": self.chargeable_weight_kg,
            "volumetric_weight_kg": self.volumetric_weight_kg,
            "weight_fee": self.weight_fee,
            "category_surcharge": self.category_surcharge,
            "packaging_surcharge": self.packaging_surcharge,
            "interstate_fee": self.interstate_fee,
            "subtotal": self.subtotal,
            "tax_amount": self.tax_amount,
            "total_price": self.total_price,
        }


def calculate_volumetric_weight(length_cm: float, width_cm: float, height_cm: float) -> float:
    """Standard IATA volumetric weight formula: (L x W x H in cm) / 5000."""
    return round((length_cm * width_cm * height_cm) / VOLUMETRIC_DIVISOR, 2)


def calculate_pricing(
    weight_kg: float,
    length_cm: float,
    width_cm: float,
    height_cm: float,
    category: ParcelCategory,
    packaging_status: str | None = None,
    pickup_state: str = "",
    receiver_state: str = "",
) -> PricingBreakdown:
    """Calculate transparent, itemized shipping price."""
    # 1. Volumetric vs dead weight
    volumetric_weight = calculate_volumetric_weight(length_cm, width_cm, height_cm)
    chargeable_weight = round(max(weight_kg, volumetric_weight), 2)

    # 2. Base fee and weight fee
    base_fee = BASE_FEE
    if chargeable_weight > BASE_WEIGHT_THRESHOLD_KG:
        extra_weight = chargeable_weight - BASE_WEIGHT_THRESHOLD_KG
        weight_fee = round(extra_weight * RATE_PER_EXTRA_KG, 2)
    else:
        weight_fee = 0.00

    # 3. Category surcharge
    cat_surcharge = CATEGORY_SURCHARGES.get(category, 0.00)

    # 4. Packaging surcharge
    pkg_surcharge = 0.00
    if packaging_status:
        pkg_surcharge = PACKAGING_SURCHARGES.get(packaging_status.upper(), 0.00)

    # 5. Interstate routing
    is_interstate = (
        bool(pickup_state.strip())
        and bool(receiver_state.strip())
        and pickup_state.strip().lower() != receiver_state.strip().lower()
    )
    interstate_fee = INTERSTATE_SURCHARGE if is_interstate else 0.00

    # 6. Subtotal and tax
    subtotal = round(base_fee + weight_fee + cat_surcharge + pkg_surcharge + interstate_fee, 2)
    tax_amount = round(subtotal * TAX_RATE_GST, 2)
    total_price = round(subtotal + tax_amount, 2)

    return PricingBreakdown(
        base_fee=base_fee,
        chargeable_weight_kg=chargeable_weight,
        volumetric_weight_kg=volumetric_weight,
        weight_fee=weight_fee,
        category_surcharge=cat_surcharge,
        packaging_surcharge=pkg_surcharge,
        interstate_fee=interstate_fee,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_price=total_price,
    )
