import unittest

import httpx

from app.main import app


class ApiSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_health_endpoint(self) -> None:
        response = await self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    async def test_profile_requires_bearer_token(self) -> None:
        response = await self.client.get("/api/v1/customers/me")
        self.assertEqual(response.status_code, 401)

    async def test_login_validates_bad_input_before_service_call(self) -> None:
        response = await self.client.post("/api/v1/auth/login", json={"email": "bad-email", "password": "short"})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
