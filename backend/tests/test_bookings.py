import time
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
import jwt

from app.core.config import Settings
from app.main import app
from app.schemas.booking import BookingStatus
from app.services.supabase import SupabaseClient


class BookingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
        self.settings = Settings(
            _env_file=None,
            supabase_url="https://test.example",
            supabase_anon_key="public-anon-key",
            supabase_jwt_algorithm="HS256",
            supabase_jwt_secret="a" * 32,
            cors_allowed_origins=["http://localhost:3000"],
        )

        patch_deps = patch("app.api.deps.get_settings", return_value=self.settings)
        patch_bookings = patch("app.api.routes.bookings.get_settings", return_value=self.settings)
        patch_supabase = patch.object(SupabaseClient, "_request", new_callable=AsyncMock)

        self.deps_mock = patch_deps.start()
        self.bookings_mock = patch_bookings.start()
        self.request = patch_supabase.start()

        self.addCleanup(patch_deps.stop)
        self.addCleanup(patch_bookings.stop)
        self.addCleanup(patch_supabase.stop)
        self.addAsyncCleanup(self.client.aclose)

        self.uid_a = str(uuid4())
        self.uid_b = str(uuid4())

        self.claims_a = {
            "sub": self.uid_a,
            "aud": "authenticated",
            "exp": int(time.time()) + 300,
            "iss": "https://test.example/auth/v1",
        }
        self.token_a = jwt.encode(self.claims_a, self.settings.supabase_jwt_secret, algorithm="HS256")
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        self.booking_id = str(uuid4())
        self.db_booking_row = {
            "id": self.booking_id,
            "tracking_number": "GCP-20261127-ABC123",
            "customer_id": self.uid_a,
            "status": "PENDING_PICKUP",
            "pickup_name": "Charan Teja",
            "pickup_phone": "+919876543210",
            "pickup_address_line_1": "123 Jubilee Hills",
            "pickup_address_line_2": "Floor 2",
            "pickup_city": "Hyderabad",
            "pickup_state": "Telangana",
            "pickup_postal_code": "500033",
            "pickup_country": "India",
            "pickup_date": "2026-11-28",
            "pickup_time_slot": "09:00 - 12:00",
            "receiver_name": "Uma Sharma",
            "receiver_phone": "+919876543211",
            "receiver_email": "uma@example.com",
            "receiver_address_line_1": "456 Indiranagar",
            "receiver_address_line_2": None,
            "receiver_city": "Bengaluru",
            "receiver_state": "Karnataka",
            "receiver_postal_code": "560038",
            "receiver_country": "India",
            "parcel_category": "electronics",
            "parcel_description": "Laptop and charger",
            "length_cm": 35.0,
            "width_cm": 25.0,
            "height_cm": 10.0,
            "estimated_weight_kg": 2.5,
            "special_instructions": "Fragile electronic equipment",
            "assigned_driver_id": None,
            "actual_weight_kg": None,
            "actual_length_cm": None,
            "actual_width_cm": None,
            "actual_height_cm": None,
            "packaging_status": None,
            "estimated_price": 450.0,
            "final_price": None,
            "created_at": "2026-11-27T10:00:00Z",
            "updated_at": "2026-11-27T10:00:00Z",
        }

        self.create_payload = {
            "pickup": {
                "name": "Charan Teja",
                "phone": "+919876543210",
                "address_line_1": "123 Jubilee Hills",
                "address_line_2": "Floor 2",
                "city": "Hyderabad",
                "state": "Telangana",
                "postal_code": "500033",
                "country": "India",
                "pickup_date": "2026-11-28",
                "pickup_time_slot": "09:00 - 12:00",
            },
            "receiver": {
                "name": "Uma Sharma",
                "phone": "+919876543211",
                "email": "uma@example.com",
                "address_line_1": "456 Indiranagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560038",
                "country": "India",
            },
            "parcel": {
                "category": "electronics",
                "description": "Laptop and charger",
                "length_cm": 35.0,
                "width_cm": 25.0,
                "height_cm": 10.0,
                "estimated_weight_kg": 2.5,
            },
            "special_instructions": "Fragile electronic equipment",
        }

    async def test_create_booking_success(self):
        self.request.return_value = [self.db_booking_row]
        response = await self.client.post("/api/v1/bookings", headers=self.headers_a, json=self.create_payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["id"], self.booking_id)
        self.assertTrue(data["tracking_number"].startswith("GCP-"))
        self.assertEqual(data["status"], "PENDING_PICKUP")
        self.assertEqual(data["customer_id"], self.uid_a)
        self.assertEqual(data["pickup"]["city"], "Hyderabad")
        self.assertEqual(data["receiver"]["city"], "Bengaluru")
        self.assertEqual(data["parcel"]["category"], "electronics")

    async def test_create_booking_validation_error(self):
        # Invalid: negative dimensions and zero weight
        bad_payload = {
            **self.create_payload,
            "parcel": {
                "category": "electronics",
                "length_cm": -5.0,
                "width_cm": 0,
                "height_cm": 10.0,
                "estimated_weight_kg": 0,
            },
        }
        response = await self.client.post("/api/v1/bookings", headers=self.headers_a, json=bad_payload)
        self.assertEqual(response.status_code, 422)

    async def test_list_my_bookings_success(self):
        self.request.return_value = [self.db_booking_row]
        response = await self.client.get("/api/v1/bookings", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["id"], self.booking_id)

    async def test_list_my_bookings_with_status_filter(self):
        self.request.return_value = [self.db_booking_row]
        response = await self.client.get("/api/v1/bookings?status=PENDING_PICKUP", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        # Verify status filter passed to Supabase REST query
        called_path = self.request.call_args_list[-1][0][1]
        self.assertIn("&status=eq.PENDING_PICKUP", called_path)

    async def test_get_booking_by_id_success(self):
        self.request.return_value = [self.db_booking_row]
        response = await self.client.get(f"/api/v1/bookings/{self.booking_id}", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.booking_id)

    async def test_get_booking_by_id_not_found(self):
        self.request.return_value = []
        response = await self.client.get(f"/api/v1/bookings/{uuid4()}", headers=self.headers_a)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Booking not found")

    async def test_cancel_booking_success(self):
        # 1st call for get_booking -> returns PENDING_PICKUP row
        # 2nd call for cancel_customer_booking RPC -> returns CANCELLED row
        cancelled_row = {**self.db_booking_row, "status": "CANCELLED"}
        self.request.side_effect = [[self.db_booking_row], cancelled_row]

        response = await self.client.post(f"/api/v1/bookings/{self.booking_id}/cancel", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "CANCELLED")
        self.assertEqual(data["id"], self.booking_id)

        # Verify that cancellation called the secure RPC endpoint rather than a direct table PATCH
        called_method = self.request.call_args_list[-1][0][0]
        called_path = self.request.call_args_list[-1][0][1]
        called_body = self.request.call_args_list[-1][0][2]
        self.assertEqual(called_method, "POST")
        self.assertEqual(called_path, "/rest/v1/rpc/cancel_customer_booking")
        self.assertEqual(called_body, {"booking_id": self.booking_id})

    async def test_cancel_booking_already_in_transit(self):
        in_transit_row = {**self.db_booking_row, "status": "IN_TRANSIT"}
        self.request.return_value = [in_transit_row]

        response = await self.client.post(f"/api/v1/bookings/{self.booking_id}/cancel", headers=self.headers_a)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot cancel booking", response.json()["detail"])

    async def test_cancel_booking_rpc_supabase_error(self):
        from app.services.supabase import SupabaseError

        self.request.side_effect = [[self.db_booking_row], SupabaseError("RPC execution failed")]
        response = await self.client.post(f"/api/v1/bookings/{self.booking_id}/cancel", headers=self.headers_a)
        self.assertEqual(response.status_code, 502)
        self.assertIn("Failed to cancel booking", response.json()["detail"])

    async def test_customer_cannot_access_other_customer_booking(self):
        """Customer B cannot view or cancel Customer A's booking."""
        claims_b = {
            "sub": self.uid_b,
            "aud": "authenticated",
            "exp": int(time.time()) + 300,
            "iss": "https://test.example/auth/v1",
        }
        token_b = jwt.encode(claims_b, self.settings.supabase_jwt_secret, algorithm="HS256")
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Supabase RLS / customer_id filter returns empty for Customer B
        self.request.return_value = []
        response = await self.client.get(f"/api/v1/bookings/{self.booking_id}", headers=headers_b)
        self.assertEqual(response.status_code, 404)

        # Verify that customer_id=eq.{uid_b} was sent, NOT uid_a
        called_path = self.request.call_args_list[-1][0][1]
        self.assertIn(f"customer_id=eq.{self.uid_b}", called_path)
        self.assertNotIn(self.uid_a, called_path)

    async def test_bookings_unauthenticated(self):
        response = await self.client.get("/api/v1/bookings")
        self.assertEqual(response.status_code, 401)

        response = await self.client.post("/api/v1/bookings", json=self.create_payload)
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
