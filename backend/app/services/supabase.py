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
