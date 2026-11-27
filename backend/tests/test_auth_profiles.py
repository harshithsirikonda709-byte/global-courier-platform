import time
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric import ec, rsa
import httpx
import jwt
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError

from app.core.config import Settings
from app.main import app
from app.services.supabase import SupabaseClient, SupabaseError


class AuthProfileTests(unittest.IsolatedAsyncioTestCase):
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
        patch_customers = patch("app.api.routes.customers.get_settings", return_value=self.settings)
        patch_auth = patch("app.api.routes.auth.get_settings", return_value=self.settings)
        patch_supabase = patch.object(SupabaseClient, "_request", new_callable=AsyncMock)

        self.deps_mock = patch_deps.start()
        self.customers_mock = patch_customers.start()
        self.auth_mock = patch_auth.start()
        self.request = patch_supabase.start()

        self.addCleanup(patch_deps.stop)
        self.addCleanup(patch_customers.stop)
        self.addCleanup(patch_auth.stop)
        self.addCleanup(patch_supabase.stop)
        self.addAsyncCleanup(self.client.aclose)

        self.uid_customer_a = str(uuid4())
        self.uid_customer_b = str(uuid4())

        self.claims_a = {
            "sub": self.uid_customer_a,
            "aud": "authenticated",
            "exp": int(time.time()) + 300,
            "iss": "https://test.example/auth/v1",
        }
        self.token_a = jwt.encode(self.claims_a, self.settings.supabase_jwt_secret, algorithm="HS256")
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        self.login_payload = {"email": "customer@example.com", "password": "password123"}
        self.session_payload = {
            "access_token": self.token_a,
            "refresh_token": "mock-refresh-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {"id": self.uid_customer_a, "email": "customer@example.com"},
        }
        self.profile_a = {
            "user_id": self.uid_customer_a,
            "email": "customer@example.com",
            "full_name": "Customer A",
            "phone": "+919876543210",
            "country": "India",
        }

    # 1. Registration tests
    async def test_register_immediate_session(self):
        data = {**self.login_payload, "full_name": "Customer A", "phone": "+919876543210"}
        self.request.return_value = self.session_payload
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["access_token"], self.token_a)
        self.assertEqual(response.json()["user_id"], self.uid_customer_a)

    async def test_register_confirmation_pending(self):
        data = {**self.login_payload, "full_name": "Customer A", "phone": "+919876543210"}
        self.request.return_value = {"id": self.uid_customer_a, "email": data["email"]}
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 202)
        body = response.json()
        self.assertTrue(body["confirmation_required"])
        self.assertIn("Check your email", body["message"])
        self.assertEqual(body["user_id"], self.uid_customer_a)
        self.assertEqual(body["email"], data["email"])
        self.assertNotIn("access_token", body)

    async def test_register_supabase_error(self):
        data = {**self.login_payload, "full_name": "Customer A"}
        self.request.side_effect = SupabaseError("User already registered")
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("User already registered", response.json()["detail"])

    async def test_register_validation_error(self):
        response = await self.client.post(
            "/api/v1/auth/register",
            json={"email": "bad@example.com", "password": "short", "full_name": "A"},
        )
        self.assertEqual(response.status_code, 422)

    async def test_register_unexpected_payload_error(self):
        data = {**self.login_payload, "full_name": "Customer A"}

        # Non-dict payload returned
        self.request.return_value = ["not", "a", "dict"]
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 502)
        self.assertIn("Unexpected response", response.json()["detail"])

        # When access_token is present but user structure is missing/malformed
        self.request.return_value = {"access_token": "token-without-user"}
        response = await self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 502)
        self.assertIn("Malformed session payload", response.json()["detail"])

    # 2. Login tests
    async def test_login_success(self):
        self.request.return_value = self.session_payload
        response = await self.client.post("/api/v1/auth/login", json=self.login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], self.uid_customer_a)
        self.request.assert_awaited_once_with("POST", "/auth/v1/token?grant_type=password", self.login_payload)

    async def test_login_invalid_credentials(self):
        self.request.side_effect = SupabaseError("Invalid login credentials")
        response = await self.client.post("/api/v1/auth/login", json=self.login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid login credentials", response.json()["detail"])

    async def test_login_validation_error(self):
        response = await self.client.post("/api/v1/auth/login", json={"email": "not-an-email", "password": "123"})
        self.assertEqual(response.status_code, 422)

    async def test_login_unexpected_payload_error(self):
        # Non-dict payload from Supabase
        self.request.return_value = None
        response = await self.client.post("/api/v1/auth/login", json=self.login_payload)
        self.assertEqual(response.status_code, 502)

        # Missing required token or user_id in payload
        self.request.return_value = {"invalid": "payload"}
        response = await self.client.post("/api/v1/auth/login", json=self.login_payload)
        self.assertEqual(response.status_code, 502)
        self.assertIn("Malformed session payload", response.json()["detail"])

    # 3. Profile retrieval and update tests
    async def test_get_my_profile_success(self):
        self.request.return_value = [self.profile_a]
        response = await self.client.get("/api/v1/customers/me", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], self.uid_customer_a)
        self.assertEqual(response.json()["full_name"], "Customer A")
        self.request.assert_awaited_with(
            "GET", f"/rest/v1/customer_profiles?user_id=eq.{self.uid_customer_a}&select=*", None, self.token_a
        )

    async def test_get_my_profile_not_found(self):
        self.request.return_value = []
        response = await self.client.get("/api/v1/customers/me", headers=self.headers_a)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Customer profile not found")

    async def test_update_my_profile_success(self):
        update_data = {"full_name": "Updated Customer A", "city": "Mumbai", "country": "India"}
        updated_profile = {**self.profile_a, **update_data}
        self.request.return_value = [updated_profile]
        response = await self.client.put("/api/v1/customers/me", headers=self.headers_a, json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["full_name"], "Updated Customer A")
        self.assertEqual(response.json()["city"], "Mumbai")
        self.request.assert_awaited_with(
            "PATCH",
            f"/rest/v1/customer_profiles?user_id=eq.{self.uid_customer_a}",
            update_data,
            self.token_a,
            {"Prefer": "return=representation"},
        )

    async def test_update_my_profile_not_found(self):
        self.request.return_value = []
        response = await self.client.put(
            "/api/v1/customers/me", headers=self.headers_a, json={"full_name": "New Name"}
        )
        self.assertEqual(response.status_code, 404)

    # 4. Customer isolation test (one customer cannot access or modify another customer's profile)
    async def test_customer_cannot_access_other_customer_profile(self):
        self.request.return_value = [self.profile_a]
        response = await self.client.get("/api/v1/customers/me", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], self.uid_customer_a)

        called_args = self.request.call_args_list[-1]
        self.assertIn(f"user_id=eq.{self.uid_customer_a}", called_args[0][1])
        self.assertNotIn(self.uid_customer_b, called_args[0][1])

        forged_claims = {
            "sub": self.uid_customer_b,
            "aud": "authenticated",
            "exp": int(time.time()) + 300,
            "iss": "https://test.example/auth/v1",
        }
        forged_token = jwt.encode(forged_claims, "wrong-secret-key-attacker-32bytes!", algorithm="HS256")
        forged_response = await self.client.get(
            "/api/v1/customers/me", headers={"Authorization": f"Bearer {forged_token}"}
        )
        self.assertEqual(forged_response.status_code, 401)

        update_data = {"full_name": "Customer A Updated"}
        self.request.return_value = [{**self.profile_a, **update_data}]
        update_response = await self.client.put("/api/v1/customers/me", headers=self.headers_a, json=update_data)
        self.assertEqual(update_response.status_code, 200)
        update_called_args = self.request.call_args_list[-1]
        self.assertIn(f"user_id=eq.{self.uid_customer_a}", update_called_args[0][1])
        self.assertNotIn(self.uid_customer_b, update_called_args[0][1])

    # 5. JWT Validation tests (claims, algorithms, JWKS errors, missing kid, malformed tokens, AUTO mode)
    async def test_jwt_claims_validation(self):
        test_cases = [
            ({"iss": "https://wrong-issuer.com/auth/v1"}, "wrong issuer"),
            ({"aud": "wrong-audience"}, "wrong audience"),
            ({"exp": int(time.time()) - 100}, "expired token"),
            ({"sub": "not-a-valid-uuid"}, "invalid uuid format for sub"),
        ]
        for claim_override, desc in test_cases:
            claims = {**self.claims_a, **claim_override}
            token = jwt.encode(claims, self.settings.supabase_jwt_secret, algorithm="HS256")
            res = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(res.status_code, 401, f"Failed on: {desc}")

        claims_no_exp = {k: v for k, v in self.claims_a.items() if k != "exp"}
        token_no_exp = jwt.encode(claims_no_exp, self.settings.supabase_jwt_secret, algorithm="HS256")
        res = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token_no_exp}"})
        self.assertEqual(res.status_code, 401)

    async def test_jwt_signing_algorithms(self):
        self.request.return_value = [self.profile_a]

        for algorithm, key in (
            ("ES256", ec.generate_private_key(ec.SECP256R1())),
            ("RS256", rsa.generate_private_key(public_exponent=65537, key_size=2048)),
        ):
            self.settings.supabase_jwt_algorithm = algorithm
            with patch("app.api.deps.project_keys") as mock_keys:
                mock_keys.return_value.get_signing_key_from_jwt.return_value = SimpleNamespace(key=key.public_key())
                token = jwt.encode(self.claims_a, key, algorithm=algorithm, headers={"kid": "test-key-id"})
                response = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"})
                self.assertEqual(response.status_code, 200)
                mock_keys.assert_called_once_with(self.claims_a["iss"])

        self.settings.supabase_jwt_algorithm = "ES256"
        token_hs = jwt.encode(self.claims_a, "secret" * 8, algorithm="HS256")
        res = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token_hs}"})
        self.assertEqual(res.status_code, 401)

    async def test_jwt_jwks_failure_and_missing_key(self):
        self.settings.supabase_jwt_algorithm = "ES256"
        key = ec.generate_private_key(ec.SECP256R1())
        token = jwt.encode(self.claims_a, key, algorithm="ES256", headers={"kid": "unknown-kid"})

        # JWKS connection error -> 503
        with patch("app.api.deps.project_keys") as mock_keys:
            mock_keys.return_value.get_signing_key_from_jwt.side_effect = PyJWKClientConnectionError("Network error")
            response = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 503)
            self.assertIn("Supabase signing keys are unavailable", response.json()["detail"])

        # Invalid or missing key ID (PyJWKClientError) -> 401
        with patch("app.api.deps.project_keys") as mock_keys:
            mock_keys.return_value.get_signing_key_from_jwt.side_effect = PyJWKClientError("Key ID not found")
            response = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 401)
            self.assertIn("Invalid or expired access token", response.json()["detail"])

    async def test_malformed_bearer_tokens(self):
        malformed_headers = [
            {},                                         # No Authorization header
            {"Authorization": "Basic dXNlcjpwYXNz"},    # Basic auth instead of Bearer
            {"Authorization": "Bearer"},                # Bearer with no space
            {"Authorization": "Bearer   "},             # Bearer with only whitespace
            {"Authorization": "Bearer not-a-jwt"},      # Invalid JWT format
            {"Authorization": "Bearer abc.def"},        # Truncated token (2 segments)
        ]
        for headers in malformed_headers:
            response = await self.client.get("/api/v1/customers/me", headers=headers)
            self.assertEqual(response.status_code, 401)

    async def test_auto_algorithm_mode(self):
        self.settings.supabase_jwt_algorithm = "AUTO"
        self.request.return_value = [self.profile_a]

        # 1. AUTO accepts valid HS256 token
        token_hs = jwt.encode(self.claims_a, self.settings.supabase_jwt_secret, algorithm="HS256")
        res_hs = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token_hs}"})
        self.assertEqual(res_hs.status_code, 200)

        # 2. AUTO accepts valid ES256 token via JWKS
        key_ec = ec.generate_private_key(ec.SECP256R1())
        token_es = jwt.encode(self.claims_a, key_ec, algorithm="ES256", headers={"kid": "ec-key"})
        with patch("app.api.deps.project_keys") as mock_keys:
            mock_keys.return_value.get_signing_key_from_jwt.return_value = SimpleNamespace(key=key_ec.public_key())
            res_es = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token_es}"})
            self.assertEqual(res_es.status_code, 200)

        # 3. AUTO rejects unsupported algorithm (e.g. none)
        token_none = jwt.encode(self.claims_a, "", algorithm="none")
        res_none = await self.client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token_none}"})
        self.assertEqual(res_none.status_code, 401)

    # 6. CORS configuration tests
    async def test_cors_configuration(self):
        s1 = Settings(_env_file=None, cors_allowed_origins="http://example.com, https://app.example.com")
        self.assertEqual(s1.cors_allowed_origins, ["http://example.com", "https://app.example.com"])

        s2 = Settings(_env_file=None, cors_allowed_origins='["http://localhost:3000", "http://localhost:5173"]')
        self.assertEqual(s2.cors_allowed_origins, ["http://localhost:3000", "http://localhost:5173"])

        s3 = Settings(_env_file=None, cors_allowed_origins="http://localhost:3000")
        self.assertEqual(s3.cors_allowed_origins, ["http://localhost:3000"])


if __name__ == "__main__":
    unittest.main()
