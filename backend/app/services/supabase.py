"""HTTP client for Supabase Auth, customer_profiles, and bookings tables."""

from typing import Any

import httpx

from app.core.config import Settings


class SupabaseError(Exception):
    pass


class SupabaseClient:
    def __init__(self, settings: Settings):
        if not settings.supabase_configured:
            raise SupabaseError("Supabase is not configured. Copy .env.example to .env and add project keys.")
        self.base_url = settings.supabase_url.rstrip("/")
        self.anon_key = settings.supabase_anon_key

    def _headers(self, access_token: str | None = None) -> dict[str, str]:
        return {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {access_token or self.anon_key}",
            "Content-Type": "application/json",
        }

    # Authentication
    async def sign_up(self, email: str, password: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/auth/v1/signup", {"email": email, "password": password, "data": metadata})

    async def sign_in(self, email: str, password: str) -> dict[str, Any]:
        return await self._request("POST", "/auth/v1/token?grant_type=password", {"email": email, "password": password})

    # Customer profiles
    async def profile(self, access_token: str, user_id: str) -> dict[str, Any] | None:
        rows = await self._request("GET", f"/rest/v1/customer_profiles?user_id=eq.{user_id}&select=*", None, access_token)
        return rows[0] if rows else None

    async def update_profile(self, access_token: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        rows = await self._request(
            "PATCH", f"/rest/v1/customer_profiles?user_id=eq.{user_id}", values, access_token,
            {"Prefer": "return=representation"},
        )
        return rows[0] if rows else None

    # Courier Bookings
    async def create_booking(self, access_token: str, record: dict[str, Any]) -> dict[str, Any]:
        rows = await self._request(
            "POST", "/rest/v1/bookings", record, access_token, {"Prefer": "return=representation"}
        )
        if not rows:
            raise SupabaseError("Failed to create booking in database")
        return rows[0]

    async def list_bookings(
        self, access_token: str, customer_id: str, status: str | None = None
    ) -> list[dict[str, Any]]:
        path = f"/rest/v1/bookings?customer_id=eq.{customer_id}&order=created_at.desc&select=*"
        if status:
            path += f"&status=eq.{status}"
        rows = await self._request("GET", path, None, access_token)
        return rows or []

    async def get_booking(self, access_token: str, booking_id: str, customer_id: str) -> dict[str, Any] | None:
        rows = await self._request(
            "GET", f"/rest/v1/bookings?id=eq.{booking_id}&customer_id=eq.{customer_id}&select=*", None, access_token
        )
        return rows[0] if rows else None

    async def update_booking(
        self, access_token: str, booking_id: str, customer_id: str, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        rows = await self._request(
            "PATCH",
            f"/rest/v1/bookings?id=eq.{booking_id}&customer_id=eq.{customer_id}",
            values,
            access_token,
            {"Prefer": "return=representation"},
        )
        return rows[0] if rows else None

    async def cancel_customer_booking(self, access_token: str, booking_id: str) -> dict[str, Any]:
        result = await self._request(
            "POST",
            "/rest/v1/rpc/cancel_customer_booking",
            {"booking_id": booking_id},
            access_token,
        )
        if not result:
            raise SupabaseError("Failed to cancel booking")
        return result if isinstance(result, dict) else result[0]

    # Day 4: Administrative and Driver Operations
    async def list_all_bookings(
        self, access_token: str, status: str | None = None, driver_id: str | None = None
    ) -> list[dict[str, Any]]:
        path = "/rest/v1/bookings?select=*&order=created_at.desc"
        if status:
            path += f"&status=eq.{status}"
        if driver_id:
            path += f"&assigned_driver_id=eq.{driver_id}"
        rows = await self._request("GET", path, None, access_token)
        return rows or []

    async def list_driver_bookings(
        self, access_token: str, driver_id: str, status: str | None = None
    ) -> list[dict[str, Any]]:
        path = f"/rest/v1/bookings?assigned_driver_id=eq.{driver_id}&select=*&order=created_at.desc"
        if status:
            path += f"&status=eq.{status}"
        rows = await self._request("GET", path, None, access_token)
        return rows or []

    async def get_booking_admin(self, access_token: str, booking_id: str) -> dict[str, Any] | None:
        rows = await self._request("GET", f"/rest/v1/bookings?id=eq.{booking_id}&select=*", None, access_token)
        return rows[0] if rows else None

    async def assign_pickup_executive(
        self, access_token: str, booking_id: str, driver_id: str
    ) -> dict[str, Any]:
        result = await self._request(
            "POST",
            "/rest/v1/rpc/assign_pickup_executive",
            {"p_booking_id": booking_id, "p_driver_id": driver_id},
            access_token,
        )
        if not result:
            raise SupabaseError("Failed to assign pickup executive")
        return result if isinstance(result, dict) else result[0]

    async def inspect_parcel_and_pickup(
        self,
        access_token: str,
        booking_id: str,
        driver_id: str,
        actual_weight: float,
        actual_length: float,
        actual_width: float,
        actual_height: float,
        packaging_status: str,
        final_price: float,
        special_instructions: str | None = None,
    ) -> dict[str, Any]:
        result = await self._request(
            "POST",
            "/rest/v1/rpc/inspect_parcel_and_pickup",
            {
                "p_booking_id": booking_id,
                "p_driver_id": driver_id,
                "p_actual_weight": actual_weight,
                "p_actual_length": actual_length,
                "p_actual_width": actual_width,
                "p_actual_height": actual_height,
                "p_packaging_status": packaging_status,
                "p_final_price": final_price,
                "p_special_instructions": special_instructions,
            },
            access_token,
        )
        if not result:
            raise SupabaseError("Failed to record parcel inspection")
        return result if isinstance(result, dict) else result[0]

    async def update_booking_workflow_status(
        self, access_token: str, booking_id: str, driver_id: str, new_status: str
    ) -> dict[str, Any]:
        result = await self._request(
            "POST",
            "/rest/v1/rpc/update_booking_workflow_status",
            {"p_booking_id": booking_id, "p_driver_id": driver_id, "p_new_status": new_status},
            access_token,
        )
        if not result:
            raise SupabaseError("Failed to update booking status")
        return result if isinstance(result, dict) else result[0]

    # Common request executor
    async def _request(
        self,
        method: str,
        path: str,
        body: Any,
        access_token: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        headers = self._headers(access_token)
        headers.update(extra_headers or {})
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.request(method, f"{self.base_url}{path}", headers=headers, json=body)
        if response.is_error:
            detail = response.json().get("msg", response.text) if response.content else "Supabase request failed"
            raise SupabaseError(detail)
        return response.json() if response.content else None
