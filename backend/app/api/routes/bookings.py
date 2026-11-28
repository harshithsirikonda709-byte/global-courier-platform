import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import bearer_token, current_user_id
from app.core.config import get_settings
from app.schemas.booking import (
    BookingCancelResponse,
    BookingCreateRequest,
    BookingListResponse,
    BookingResponse,
    BookingStatus,
    ParcelCategory,
    ParcelDetails,
    PickupDetails,
    ReceiverDetails,
)
from app.services.supabase import SupabaseClient, SupabaseError

router = APIRouter(prefix="/bookings", tags=["Courier Bookings"])


def generate_tracking_number() -> str:
    """Generate a human-readable unique tracking identifier."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_suffix = uuid.uuid4().hex[:6].upper()
    return f"GCP-{date_str}-{random_suffix}"


def to_db_record(data: BookingCreateRequest, customer_id: str, tracking_number: str) -> dict[str, Any]:
    """Map the nested request model into flat database columns."""
    return {
        "tracking_number": tracking_number,
        "customer_id": customer_id,
        "status": BookingStatus.PENDING_PICKUP.value,
        "pickup_name": data.pickup.name,
        "pickup_phone": data.pickup.phone,
        "pickup_address_line_1": data.pickup.address_line_1,
        "pickup_address_line_2": data.pickup.address_line_2,
        "pickup_city": data.pickup.city,
        "pickup_state": data.pickup.state,
        "pickup_postal_code": data.pickup.postal_code,
        "pickup_country": data.pickup.country,
        "pickup_date": data.pickup.pickup_date.isoformat() if data.pickup.pickup_date else None,
        "pickup_time_slot": data.pickup.pickup_time_slot,
        "receiver_name": data.receiver.name,
        "receiver_phone": data.receiver.phone,
        "receiver_email": data.receiver.email,
        "receiver_address_line_1": data.receiver.address_line_1,
        "receiver_address_line_2": data.receiver.address_line_2,
        "receiver_city": data.receiver.city,
        "receiver_state": data.receiver.state,
        "receiver_postal_code": data.receiver.postal_code,
        "receiver_country": data.receiver.country,
        "parcel_category": data.parcel.category.value,
        "parcel_description": data.parcel.description,
        "length_cm": data.parcel.length_cm,
        "width_cm": data.parcel.width_cm,
        "height_cm": data.parcel.height_cm,
        "estimated_weight_kg": data.parcel.estimated_weight_kg,
        "special_instructions": data.special_instructions,
    }


def to_booking_response(row: dict[str, Any]) -> BookingResponse:
    """Map database row into structured response model."""
    return BookingResponse(
        id=str(row["id"]),
        tracking_number=row["tracking_number"],
        customer_id=str(row["customer_id"]),
        status=BookingStatus(row["status"]),
        pickup=PickupDetails(
            name=row["pickup_name"],
            phone=row["pickup_phone"],
            address_line_1=row["pickup_address_line_1"],
            address_line_2=row.get("pickup_address_line_2"),
            city=row["pickup_city"],
            state=row["pickup_state"],
            postal_code=row["pickup_postal_code"],
            country=row.get("pickup_country") or "India",
            pickup_date=row.get("pickup_date"),
            pickup_time_slot=row.get("pickup_time_slot"),
        ),
        receiver=ReceiverDetails(
            name=row["receiver_name"],
            phone=row["receiver_phone"],
            email=row.get("receiver_email"),
            address_line_1=row["receiver_address_line_1"],
            address_line_2=row.get("receiver_address_line_2"),
            city=row["receiver_city"],
            state=row["receiver_state"],
            postal_code=row["receiver_postal_code"],
            country=row.get("receiver_country") or "India",
        ),
        parcel=ParcelDetails(
            category=ParcelCategory(row["parcel_category"]),
            description=row.get("parcel_description"),
            length_cm=float(row["length_cm"]),
            width_cm=float(row["width_cm"]),
            height_cm=float(row["height_cm"]),
            estimated_weight_kg=float(row["estimated_weight_kg"]),
        ),
        special_instructions=row.get("special_instructions"),
        assigned_driver_id=str(row["assigned_driver_id"]) if row.get("assigned_driver_id") else None,
        actual_weight_kg=float(row["actual_weight_kg"]) if row.get("actual_weight_kg") is not None else None,
        actual_length_cm=float(row["actual_length_cm"]) if row.get("actual_length_cm") is not None else None,
        actual_width_cm=float(row["actual_width_cm"]) if row.get("actual_width_cm") is not None else None,
        actual_height_cm=float(row["actual_height_cm"]) if row.get("actual_height_cm") is not None else None,
        packaging_status=row.get("packaging_status"),
        estimated_price=float(row["estimated_price"]) if row.get("estimated_price") is not None else None,
        final_price=float(row["final_price"]) if row.get("final_price") is not None else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreateRequest,
    user_id: str = Depends(current_user_id),
    token: str = Depends(bearer_token),
) -> BookingResponse:
    """Create a new courier booking for the authenticated customer."""
    tracking_number = generate_tracking_number()
    record = to_db_record(data, user_id, tracking_number)
    try:
        created_row = await SupabaseClient(get_settings()).create_booking(token, record)
        return to_booking_response(created_row)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to create booking: {exc}")


@router.get("", response_model=BookingListResponse)
async def list_customer_bookings(
    status_filter: BookingStatus | None = Query(default=None, alias="status", description="Filter by booking status"),
    user_id: str = Depends(current_user_id),
    token: str = Depends(bearer_token),
) -> BookingListResponse:
    """List all courier bookings for the authenticated customer."""
    try:
        rows = await SupabaseClient(get_settings()).list_bookings(
            token, user_id, status_filter.value if status_filter else None
        )
        items = [to_booking_response(row) for row in rows]
        return BookingListResponse(items=items, total=len(items))
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch bookings: {exc}")


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking_by_id(
    booking_id: str,
    user_id: str = Depends(current_user_id),
    token: str = Depends(bearer_token),
) -> BookingResponse:
    """Retrieve details of a specific booking owned by the authenticated customer."""
    try:
        row = await SupabaseClient(get_settings()).get_booking(token, booking_id, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")
        return to_booking_response(row)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Database query failed: {exc}")


@router.post("/{booking_id}/cancel", response_model=BookingCancelResponse)
async def cancel_booking(
    booking_id: str,
    user_id: str = Depends(current_user_id),
    token: str = Depends(bearer_token),
) -> BookingCancelResponse:
    """Cancel a booking if it is still pending pickup using secure database RPC."""
    client = SupabaseClient(get_settings())
    try:
        row = await client.get_booking(token, booking_id, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")

        current_status = row.get("status")
        if current_status != BookingStatus.PENDING_PICKUP.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel booking with status '{current_status}'. Only '{BookingStatus.PENDING_PICKUP.value}' bookings can be cancelled.",
            )

        updated_row = await client.cancel_customer_booking(token, booking_id)
        return BookingCancelResponse(
            id=str(updated_row["id"]),
            tracking_number=updated_row["tracking_number"],
            status=BookingStatus.CANCELLED,
            message="Booking cancelled successfully",
        )
    except HTTPException:
        raise
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to cancel booking: {exc}")
