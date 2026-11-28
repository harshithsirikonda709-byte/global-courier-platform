from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class BookingStatus(str, Enum):
    PENDING_PICKUP = "PENDING_PICKUP"
    PICKUP_ASSIGNED = "PICKUP_ASSIGNED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ParcelCategory(str, Enum):
    DOCUMENT = "document"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FRAGILE = "fragile"
    PERISHABLE = "perishable"
    GENERAL = "general"


class PickupDetails(BaseModel):
    name: str = Field(min_length=2, max_length=120, description="Contact name at pickup location")
    phone: str = Field(min_length=7, max_length=20, description="Contact phone at pickup location")
    address_line_1: str = Field(min_length=3, max_length=200, description="Pickup street address line 1")
    address_line_2: str | None = Field(default=None, max_length=200, description="Pickup address line 2 (apartment/suite)")
    city: str = Field(min_length=2, max_length=100, description="Pickup city")
    state: str = Field(min_length=2, max_length=100, description="Pickup state or province")
    postal_code: str = Field(min_length=3, max_length=20, description="Pickup postal or PIN code")
    country: str = Field(default="India", max_length=100, description="Pickup country")
    pickup_date: date | None = Field(default=None, description="Requested pickup date")
    pickup_time_slot: str | None = Field(default=None, description="Preferred time slot (e.g. 09:00 - 12:00)")


class ReceiverDetails(BaseModel):
    name: str = Field(min_length=2, max_length=120, description="Recipient full name")
    phone: str = Field(min_length=7, max_length=20, description="Recipient phone number")
    email: EmailStr | None = Field(default=None, description="Recipient email for delivery notifications")
    address_line_1: str = Field(min_length=3, max_length=200, description="Delivery street address line 1")
    address_line_2: str | None = Field(default=None, max_length=200, description="Delivery address line 2")
    city: str = Field(min_length=2, max_length=100, description="Delivery city")
    state: str = Field(min_length=2, max_length=100, description="Delivery state or province")
    postal_code: str = Field(min_length=3, max_length=20, description="Delivery postal or PIN code")
    country: str = Field(default="India", max_length=100, description="Delivery country")


class ParcelDetails(BaseModel):
    category: ParcelCategory = Field(description="Category of the parcel")
    description: str | None = Field(default=None, max_length=500, description="Brief description of parcel contents")
    length_cm: float = Field(gt=0, le=500, description="Package length in centimeters")
    width_cm: float = Field(gt=0, le=500, description="Package width in centimeters")
    height_cm: float = Field(gt=0, le=500, description="Package height in centimeters")
    estimated_weight_kg: float = Field(gt=0, le=1000, description="Estimated parcel weight in kilograms")


class BookingCreateRequest(BaseModel):
    pickup: PickupDetails
    receiver: ReceiverDetails
    parcel: ParcelDetails
    special_instructions: str | None = Field(default=None, max_length=1000, description="Special handling or delivery notes")


class BookingResponse(BaseModel):
    id: str
    tracking_number: str
    customer_id: str
    status: BookingStatus
    pickup: PickupDetails
    receiver: ReceiverDetails
    parcel: ParcelDetails
    special_instructions: str | None = None

    # Day 4 fields
    assigned_driver_id: str | None = None
    actual_weight_kg: float | None = None
    actual_length_cm: float | None = None
    actual_width_cm: float | None = None
    actual_height_cm: float | None = None
    packaging_status: str | None = None
    estimated_price: float | None = None
    final_price: float | None = None

    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseModel):
    items: list[BookingResponse]
    total: int


class BookingCancelResponse(BaseModel):
    id: str
    tracking_number: str
    status: BookingStatus = BookingStatus.CANCELLED
    message: str = "Booking cancelled successfully"


class PackagingStatus(str, Enum):
    ORIGINAL = "ORIGINAL"
    REPACKAGED = "REPACKAGED"
    CUSTOM_CRATING = "CUSTOM_CRATING"
    DAMAGED = "DAMAGED"


class PickupAssignRequest(BaseModel):
    driver_id: str = Field(min_length=36, max_length=36, description="UUID of the assigned pickup executive")


class PickupAssignResponse(BaseModel):
    id: str
    tracking_number: str
    status: BookingStatus
    assigned_driver_id: str
    message: str = "Pickup executive assigned successfully"


class ParcelInspectRequest(BaseModel):
    actual_weight_kg: float = Field(gt=0, le=1000, description="Inspected dead weight in kilograms")
    actual_length_cm: float = Field(gt=0, le=500, description="Inspected length in centimeters")
    actual_width_cm: float = Field(gt=0, le=500, description="Inspected width in centimeters")
    actual_height_cm: float = Field(gt=0, le=500, description="Inspected height in centimeters")
    packaging_status: PackagingStatus = Field(description="Packaging status determined during inspection")
    special_instructions: str | None = Field(default=None, max_length=1000, description="Updated handling instructions")


class ParcelInspectResponse(BaseModel):
    id: str
    tracking_number: str
    status: BookingStatus
    actual_weight_kg: float
    actual_length_cm: float
    actual_width_cm: float
    actual_height_cm: float
    packaging_status: str
    final_price: float
    message: str = "Parcel inspection completed and final price computed successfully"


class BookingStatusUpdateRequest(BaseModel):
    status: BookingStatus = Field(description="Target booking status")
    notes: str | None = Field(default=None, max_length=500, description="Status update or delivery notes")


class BookingStatusUpdateResponse(BaseModel):
    id: str
    tracking_number: str
    status: BookingStatus
    updated_at: datetime
    message: str = "Booking status updated successfully"
