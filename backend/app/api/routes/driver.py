from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import bearer_token, current_user_id, require_driver
from app.api.routes.bookings import to_booking_response
from app.core.config import get_settings
from app.schemas.booking import (
    BookingListResponse,
    BookingResponse,
    BookingStatus,
    BookingStatusUpdateRequest,
    BookingStatusUpdateResponse,
    ParcelCategory,
    ParcelInspectRequest,
    ParcelInspectResponse,
)
from app.services.pricing import calculate_pricing
from app.services.supabase import SupabaseClient, SupabaseError

router = APIRouter(prefix="/driver", tags=["Pickup Executive & Driver Operations"])


@router.get("/bookings", response_model=BookingListResponse)
async def list_assigned_bookings(
    status_filter: BookingStatus | None = Query(default=None, alias="status", description="Filter by booking status"),
    token: str = Depends(bearer_token),
    driver_id: str = Depends(current_user_id),
    _driver: dict[str, Any] = Depends(require_driver),
) -> BookingListResponse:
    """List all courier bookings assigned to the authenticated pickup executive."""
    try:
        rows = await SupabaseClient(get_settings()).list_driver_bookings(
            token, driver_id, status=status_filter.value if status_filter else None
        )
        items = [to_booking_response(row) for row in rows]
        return BookingListResponse(items=items, total=len(items))
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Database query failed: {exc}")


@router.post("/bookings/{booking_id}/inspect", response_model=ParcelInspectResponse)
async def inspect_parcel(
    booking_id: str,
    data: ParcelInspectRequest,
    token: str = Depends(bearer_token),
    driver_id: str = Depends(current_user_id),
    _driver: dict[str, Any] = Depends(require_driver),
) -> ParcelInspectResponse:
    """Record physical parcel inspection measurements upon pickup and calculate final price.

    Updates actual weight, dimensions, and packaging condition. Automatically calculates
    final price through the pricing engine and transitions status to PICKED_UP.
    """
    client = SupabaseClient(get_settings())
    try:
        # Retrieve booking to inspect current state, category, and locations
        booking = await client.get_booking_admin(token, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if str(booking.get("assigned_driver_id")) != driver_id:
            raise HTTPException(status_code=403, detail="Forbidden: Booking is not assigned to you")

        current_status = booking.get("status")
        if current_status != BookingStatus.PICKUP_ASSIGNED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot inspect booking with status '{current_status}'. Status must be '{BookingStatus.PICKUP_ASSIGNED.value}'.",
            )

        # Calculate final price using actual inspected measurements
        category = ParcelCategory(booking["parcel_category"])
        pickup_state = booking.get("pickup_state") or ""
        receiver_state = booking.get("receiver_state") or ""

        pricing = calculate_pricing(
            weight_kg=data.actual_weight_kg,
            length_cm=data.actual_length_cm,
            width_cm=data.actual_width_cm,
            height_cm=data.actual_height_cm,
            category=category,
            packaging_status=data.packaging_status.value,
            pickup_state=pickup_state,
            receiver_state=receiver_state,
        )

        # Call database RPC
        updated_row = await client.inspect_parcel_and_pickup(
            access_token=token,
            booking_id=booking_id,
            driver_id=driver_id,
            actual_weight=data.actual_weight_kg,
            actual_length=data.actual_length_cm,
            actual_width=data.actual_width_cm,
            actual_height=data.actual_height_cm,
            packaging_status=data.packaging_status.value,
            final_price=pricing.total_price,
            special_instructions=data.special_instructions,
        )

        return ParcelInspectResponse(
            id=str(updated_row["id"]),
            tracking_number=updated_row["tracking_number"],
            status=BookingStatus(updated_row["status"]),
            actual_weight_kg=float(updated_row["actual_weight_kg"]),
            actual_length_cm=float(updated_row["actual_length_cm"]),
            actual_width_cm=float(updated_row["actual_width_cm"]),
            actual_height_cm=float(updated_row["actual_height_cm"]),
            packaging_status=str(updated_row["packaging_status"]),
            final_price=float(updated_row["final_price"]),
            message="Parcel inspection completed and final price computed successfully",
        )
    except HTTPException:
        raise
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to record parcel inspection: {exc}")


@router.patch("/bookings/{booking_id}/status", response_model=BookingStatusUpdateResponse)
async def update_delivery_status(
    booking_id: str,
    data: BookingStatusUpdateRequest,
    token: str = Depends(bearer_token),
    driver_id: str = Depends(current_user_id),
    _driver: dict[str, Any] = Depends(require_driver),
) -> BookingStatusUpdateResponse:
    """Transition courier booking delivery status along the delivery lifecycle.

    Supported transitions:
    - PICKED_UP -> IN_TRANSIT
    - IN_TRANSIT -> OUT_FOR_DELIVERY
    - OUT_FOR_DELIVERY -> DELIVERED
    """
    client = SupabaseClient(get_settings())
    try:
        booking = await client.get_booking_admin(token, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if str(booking.get("assigned_driver_id")) != driver_id:
            raise HTTPException(status_code=403, detail="Forbidden: Booking is not assigned to you")

        current_status = booking.get("status")

        # Validate workflow transitions
        valid_transitions = {
            BookingStatus.PICKED_UP.value: [BookingStatus.IN_TRANSIT.value, BookingStatus.CANCELLED.value],
            BookingStatus.IN_TRANSIT.value: [BookingStatus.OUT_FOR_DELIVERY.value, BookingStatus.CANCELLED.value],
            BookingStatus.OUT_FOR_DELIVERY.value: [BookingStatus.DELIVERED.value, BookingStatus.CANCELLED.value],
        }

        allowed_next = valid_transitions.get(current_status, [])
        if data.status.value not in allowed_next:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from '{current_status}' to '{data.status.value}'. Allowed: {allowed_next}",
            )

        updated_row = await client.update_booking_workflow_status(
            access_token=token,
            booking_id=booking_id,
            driver_id=driver_id,
            new_status=data.status.value,
        )

        return BookingStatusUpdateResponse(
            id=str(updated_row["id"]),
            tracking_number=updated_row["tracking_number"],
            status=BookingStatus(updated_row["status"]),
            updated_at=updated_row["updated_at"],
            message=f"Booking status transitioned to {data.status.value}",
        )
    except HTTPException:
        raise
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to update booking status: {exc}")
