from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import bearer_token, require_admin
from app.api.routes.bookings import to_booking_response
from app.core.config import get_settings
from app.schemas.booking import (
    BookingListResponse,
    BookingResponse,
    BookingStatus,
    PickupAssignRequest,
    PickupAssignResponse,
)
from app.services.supabase import SupabaseClient, SupabaseError

router = APIRouter(prefix="/admin", tags=["Admin Pickup Management"])


@router.get("/bookings", response_model=BookingListResponse)
async def list_all_bookings(
    status_filter: BookingStatus | None = Query(default=None, alias="status", description="Filter by booking status"),
    driver_id: str | None = Query(default=None, description="Filter by assigned pickup executive ID"),
    token: str = Depends(bearer_token),
    _admin: dict[str, Any] = Depends(require_admin),
) -> BookingListResponse:
    """List all courier bookings in the platform with optional status and driver filtering.

    Requires administrative authorization.
    """
    try:
        rows = await SupabaseClient(get_settings()).list_all_bookings(
            token,
            status=status_filter.value if status_filter else None,
            driver_id=driver_id,
        )
        items = [to_booking_response(row) for row in rows]
        return BookingListResponse(items=items, total=len(items))
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Database query failed: {exc}")


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking_details(
    booking_id: str,
    token: str = Depends(bearer_token),
    _admin: dict[str, Any] = Depends(require_admin),
) -> BookingResponse:
    """Retrieve full details of any booking.

    Requires administrative authorization.
    """
    try:
        row = await SupabaseClient(get_settings()).get_booking_admin(token, booking_id)
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")
        return to_booking_response(row)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Database query failed: {exc}")


@router.post("/bookings/{booking_id}/assign", response_model=PickupAssignResponse)
async def assign_pickup_executive(
    booking_id: str,
    data: PickupAssignRequest,
    token: str = Depends(bearer_token),
    _admin: dict[str, Any] = Depends(require_admin),
) -> PickupAssignResponse:
    """Assign a pickup executive to a courier booking.

    Transitions booking status from PENDING_PICKUP to PICKUP_ASSIGNED.
    Requires administrative authorization.
    """
    try:
        UUID(data.driver_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid driver_id format. Must be a valid UUID.")

    client = SupabaseClient(get_settings())
    try:
        # Check that booking exists and is in assignable status
        booking = await client.get_booking_admin(token, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        current_status = booking.get("status")
        if current_status not in (BookingStatus.PENDING_PICKUP.value, BookingStatus.PICKUP_ASSIGNED.value):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot assign pickup executive to booking with status '{current_status}'. Must be in 'PENDING_PICKUP' or 'PICKUP_ASSIGNED'.",
            )

        updated_row = await client.assign_pickup_executive(token, booking_id, data.driver_id)
        return PickupAssignResponse(
            id=str(updated_row["id"]),
            tracking_number=updated_row["tracking_number"],
            status=BookingStatus(updated_row["status"]),
            assigned_driver_id=str(updated_row["assigned_driver_id"]),
            message="Pickup executive assigned successfully",
        )
    except HTTPException:
        raise
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to assign pickup executive: {exc}")
