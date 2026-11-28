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


class PickupProcessingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
        self.settings = Settings(
            _env_file=None,
            supabase_url="https://test.example",
            supabase_anon_key="public-anon-key",
            supabase_jwt_algorithm="HS256",
            supabase_jwt_secret="b" * 32,
            cors_allowed_origins=["http://localhost:3000"],
        )

        patch_deps = patch("app.api.deps.get_settings", return_value=self.settings)
        patch_admin = patch("app.api.routes.admin.get_settings", return_value=self.settings)
        patch_driver = patch("app.api.routes.driver.get_settings", return_value=self.settings)
        patch_supabase = patch.object(SupabaseClient, "_request", new_callable=AsyncMock)

        self.deps_mock = patch_deps.start()
        self.admin_mock = patch_admin.start()
        self.driver_mock = patch_driver.start()
        self.request = patch_supabase.start()

        self.addCleanup(patch_deps.stop)
        self.addCleanup(patch_admin.stop)
        self.addCleanup(patch_driver.stop)
        self.addCleanup(patch_supabase.stop)
        self.addAsyncCleanup(self.client.aclose)

        # Users & tokens
        self.admin_id = str(uuid4())
        self.driver_id = str(uuid4())
        self.other_driver_id = str(uuid4())
        self.customer_id = str(uuid4())
        self.booking_id = str(uuid4())

        self.admin_token = jwt.encode(
            {"sub": self.admin_id, "aud": "authenticated", "exp": int(time.time()) + 300, "iss": "https://test.example/auth/v1", "role": "admin"},
            self.settings.supabase_jwt_secret,
            algorithm="HS256",
        )
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        self.driver_token = jwt.encode(
            {"sub": self.driver_id, "aud": "authenticated", "exp": int(time.time()) + 300, "iss": "https://test.example/auth/v1", "user_metadata": {"role": "driver"}},
            self.settings.supabase_jwt_secret,
            algorithm="HS256",
        )
        self.driver_headers = {"Authorization": f"Bearer {self.driver_token}"}

        self.customer_token = jwt.encode(
            {"sub": self.customer_id, "aud": "authenticated", "exp": int(time.time()) + 300, "iss": "https://test.example/auth/v1", "user_metadata": {"role": "customer"}},
            self.settings.supabase_jwt_secret,
            algorithm="HS256",
        )
        self.customer_headers = {"Authorization": f"Bearer {self.customer_token}"}

        self.base_booking_row = {
            "id": self.booking_id,
            "tracking_number": "GCP-20261128-DAY401",
            "customer_id": self.customer_id,
            "status": "PENDING_PICKUP",
            "pickup_name": "Charan Teja",
            "pickup_phone": "+919876543210",
            "pickup_address_line_1": "123 Jubilee Hills",
            "pickup_address_line_2": None,
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
            "parcel_description": "Laptop and accessories",
            "length_cm": 35.0,
            "width_cm": 25.0,
            "height_cm": 10.0,
            "estimated_weight_kg": 2.5,
            "special_instructions": "Handle with care",
            "assigned_driver_id": None,
            "actual_weight_kg": None,
            "actual_length_cm": None,
            "actual_width_cm": None,
            "actual_height_cm": None,
            "packaging_status": None,
            "estimated_price": 450.0,
            "final_price": None,
            "created_at": "2026-11-28T10:00:00Z",
            "updated_at": "2026-11-28T10:00:00Z",
        }

    # =========================================================================
    # Admin Assignment Tests
    # =========================================================================
    async def test_admin_assign_pickup_executive_success(self):
        # 1. get_booking_admin -> returns PENDING_PICKUP row
        # 2. assign_pickup_executive RPC -> returns updated row
        assigned_row = {
            **self.base_booking_row,
            "status": "PICKUP_ASSIGNED",
            "assigned_driver_id": self.driver_id,
        }
        self.request.side_effect = [[self.base_booking_row], assigned_row]

        response = await self.client.post(
            f"/api/v1/admin/bookings/{self.booking_id}/assign",
            headers=self.admin_headers,
            json={"driver_id": self.driver_id},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "PICKUP_ASSIGNED")
        self.assertEqual(data["assigned_driver_id"], self.driver_id)
        self.assertEqual(data["id"], self.booking_id)

    async def test_admin_assign_requires_admin_role(self):
        # Customer attempting to call admin assignment endpoint must be rejected with 403
        response = await self.client.post(
            f"/api/v1/admin/bookings/{self.booking_id}/assign",
            headers=self.customer_headers,
            json={"driver_id": self.driver_id},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Admin access required", response.json()["detail"])

    async def test_admin_assign_invalid_status_rejected(self):
        delivered_row = {**self.base_booking_row, "status": "DELIVERED"}
        self.request.return_value = [delivered_row]

        response = await self.client.post(
            f"/api/v1/admin/bookings/{self.booking_id}/assign",
            headers=self.admin_headers,
            json={"driver_id": self.driver_id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot assign pickup executive", response.json()["detail"])

    async def test_admin_list_bookings_success(self):
        self.request.return_value = [self.base_booking_row]
        response = await self.client.get("/api/v1/admin/bookings?status=PENDING_PICKUP", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)

    # =========================================================================
    # Driver Operations Tests
    # =========================================================================
    async def test_driver_list_assigned_bookings(self):
        assigned_row = {**self.base_booking_row, "status": "PICKUP_ASSIGNED", "assigned_driver_id": self.driver_id}
        self.request.return_value = [assigned_row]

        response = await self.client.get("/api/v1/driver/bookings", headers=self.driver_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["assigned_driver_id"], self.driver_id)

    async def test_driver_operations_forbidden_for_customer(self):
        response = await self.client.get("/api/v1/driver/bookings", headers=self.customer_headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Pickup executive access required", response.json()["detail"])

    async def test_driver_inspect_parcel_success(self):
        # Booking currently in PICKUP_ASSIGNED status with this driver
        assigned_row = {
            **self.base_booking_row,
            "status": "PICKUP_ASSIGNED",
            "assigned_driver_id": self.driver_id,
        }
        inspected_row = {
            **assigned_row,
            "status": "PICKED_UP",
            "actual_weight_kg": 2.8,
            "actual_length_cm": 36.0,
            "actual_width_cm": 26.0,
            "actual_height_cm": 12.0,
            "packaging_status": "REPACKAGED",
            "final_price": 530.0,
        }
        # 1. get_booking_admin -> assigned_row
        # 2. inspect_parcel_and_pickup RPC -> inspected_row
        self.request.side_effect = [[assigned_row], inspected_row]

        payload = {
            "actual_weight_kg": 2.8,
            "actual_length_cm": 36.0,
            "actual_width_cm": 26.0,
            "actual_height_cm": 12.0,
            "packaging_status": "REPACKAGED",
            "special_instructions": "Repackaged with reinforced corners",
        }
        response = await self.client.post(
            f"/api/v1/driver/bookings/{self.booking_id}/inspect",
            headers=self.driver_headers,
            json=payload,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "PICKED_UP")
        self.assertEqual(data["actual_weight_kg"], 2.8)
        self.assertEqual(data["packaging_status"], "REPACKAGED")
        self.assertGreater(data["final_price"], 0)

    async def test_driver_inspect_unassigned_booking_forbidden(self):
        # Booking assigned to another driver
        other_driver_booking = {
            **self.base_booking_row,
            "status": "PICKUP_ASSIGNED",
            "assigned_driver_id": self.other_driver_id,
        }
        self.request.return_value = [other_driver_booking]

        payload = {
            "actual_weight_kg": 2.8,
            "actual_length_cm": 36.0,
            "actual_width_cm": 26.0,
            "actual_height_cm": 12.0,
            "packaging_status": "ORIGINAL",
        }
        response = await self.client.post(
            f"/api/v1/driver/bookings/{self.booking_id}/inspect",
            headers=self.driver_headers,
            json=payload,
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("not assigned to you", response.json()["detail"])

    async def test_driver_update_delivery_status_chain(self):
        # Test transition: PICKED_UP -> IN_TRANSIT
        picked_up_row = {
            **self.base_booking_row,
            "status": "PICKED_UP",
            "assigned_driver_id": self.driver_id,
        }
        in_transit_row = {**picked_up_row, "status": "IN_TRANSIT"}
        self.request.side_effect = [[picked_up_row], in_transit_row]

        response = await self.client.patch(
            f"/api/v1/driver/bookings/{self.booking_id}/status",
            headers=self.driver_headers,
            json={"status": "IN_TRANSIT", "notes": "Departed Hyderabad hub"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "IN_TRANSIT")

    async def test_driver_update_status_invalid_transition(self):
        # Cannot transition directly from PICKED_UP to DELIVERED
        picked_up_row = {
            **self.base_booking_row,
            "status": "PICKED_UP",
            "assigned_driver_id": self.driver_id,
        }
        self.request.return_value = [picked_up_row]

        response = await self.client.patch(
            f"/api/v1/driver/bookings/{self.booking_id}/status",
            headers=self.driver_headers,
            json={"status": "DELIVERED"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid status transition", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
