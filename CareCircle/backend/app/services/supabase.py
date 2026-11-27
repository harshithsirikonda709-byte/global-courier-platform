from typing import Any

import httpx

from ..config import Settings


class SupabaseError(Exception):
    pass


class SupabaseClient:
    def __init__(self, settings: Settings):
        if not settings.supabase_configured:
            raise SupabaseError("Supabase authentication is not configured.")
        self.base_url = settings.supabase_url.rstrip("/")
        self.anon_key = settings.supabase_anon_key

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
        }

    async def sign_up(self, email: str, password: str, metadata: dict[str, Any]) -> Any:
        return await self._request(
            "POST",
            "/auth/v1/signup",
            {"email": email, "password": password, "data": metadata},
        )

    async def sign_in(self, email: str, password: str) -> Any:
        return await self._request(
            "POST",
            "/auth/v1/token?grant_type=password",
            {"email": email, "password": password},
        )

    async def _request(self, method: str, path: str, body: Any) -> Any:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.request(
                    method,
                    f"{self.base_url}{path}",
                    headers=self._headers(),
                    json=body,
                )
        except httpx.RequestError as exc:
            raise SupabaseError("Supabase authentication service is unavailable.") from exc

        if response.is_error:
            try:
                error = response.json()
            except ValueError:
                error = {}
            detail = error.get("msg") or error.get("message") or "Supabase authentication failed"
            raise SupabaseError(str(detail))
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise SupabaseError("Supabase returned an invalid response.") from exc
