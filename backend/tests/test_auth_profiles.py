import time
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives.asymmetric import ec, rsa
import httpx

from app.core.config import Settings
from app.main import app
from app.services.supabase import SupabaseClient


class AuthProfileTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
        self.addAsyncCleanup(self.client.aclose)
        self.settings = Settings(_env_file=None, supabase_url="https://test.example",
                                 supabase_anon_key="public", supabase_jwt_algorithm="HS256",
                                 supabase_jwt_secret="a" * 32)
        for module in ("app.api.deps", "app.api.routes.customers", "app.api.routes.auth"):
            self.enterContext(patch(module + ".get_settings", return_value=self.settings))
        self.request = self.enterContext(patch.object(SupabaseClient, "_request", new_callable=AsyncMock))
        self.uid = str(uuid4())
        self.claims = dict(sub=self.uid, aud="authenticated", exp=int(time.time()) + 300,
                           iss="https://test.example/auth/v1")
        self.token = jwt.encode(self.claims, self.settings.supabase_jwt_secret, algorithm="HS256")
        self.headers = {"Authorization": "Bearer " + self.token}
        self.login = {"email": "customer@example.com", "password": "test-password"}
        self.session = {"access_token": self.token, "user": {"id": self.uid}}
        self.profile = {"user_id": self.uid, "email": self.login["email"], "full_name": "Test Customer"}

    async def test_register(self):
        data = {**self.login, "full_name": "Test Customer"}
        self.request.return_value = self.session
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["access_token"], self.token)
        self.request.return_value = {"id": self.uid}
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.json()["confirmation_required"])
        self.assertNotIn("access_token", response.json())

    async def test_login(self):
        self.request.return_value = self.session
        response = await self.client.post("/api/v1/auth/login", json=self.login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], self.uid)
        self.request.assert_awaited_once_with("POST", "/auth/v1/token?grant_type=password", self.login)

    async def test_get_and_update_use_authenticated_identity(self):
        self.request.return_value = [self.profile]
        url = "/api/v1/customers/me"
        response = await self.client.get(url, headers=self.headers)
        self.assertEqual(response.json()["user_id"], self.uid)
        self.request.assert_awaited_with("GET", f"/rest/v1/customer_profiles?user_id=eq.{self.uid}&select=*",
                                         None, self.token)
        data = {"full_name": "Updated Name"}
        self.request.return_value = [{**self.profile, **data}]
        response = await self.client.put(url, headers=self.headers, json=data)
        self.assertEqual(response.json()["full_name"], "Updated Name")
        self.request.assert_awaited_with("PATCH", f"/rest/v1/customer_profiles?user_id=eq.{self.uid}",
                                         data, self.token, {"Prefer": "return=representation"})

    async def test_required_claims(self):
        for change in ({"iss": "other"}, {"aud": "other"}, {"exp": 0}, {"sub": "invalid"}, {}):
            claims = {**self.claims, **change}
            if not change:
                del claims["exp"]
            token = jwt.encode(claims, self.settings.supabase_jwt_secret, algorithm="HS256")
            response = await self.client.get("/api/v1/customers/me", headers={"Authorization": "Bearer " + token})
            self.assertEqual(response.status_code, 401)
        self.request.assert_not_awaited()

    async def test_project_signing_algorithms(self):
        self.request.return_value = [self.profile]
        for algorithm, key in (("ES256", ec.generate_private_key(ec.SECP256R1())),
                               ("RS256", rsa.generate_private_key(public_exponent=65537, key_size=2048))):
            self.settings.supabase_jwt_algorithm = algorithm
            with patch("app.api.deps.project_keys") as keys:
                keys.return_value.get_signing_key_from_jwt.return_value = SimpleNamespace(key=key.public_key())
                token = jwt.encode(self.claims, key, algorithm=algorithm, headers={"kid": "test"})
                response = await self.client.get("/api/v1/customers/me", headers={"Authorization": "Bearer " + token})
                self.assertEqual(response.status_code, 200)
                keys.assert_called_once_with(self.claims["iss"])
