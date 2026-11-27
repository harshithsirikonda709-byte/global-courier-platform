import unittest
from datetime import datetime, timezone
from time import time
from unittest.mock import patch

from fastapi.testclient import TestClient
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user
from app.config import Settings
from app.database import Base, get_db
from app.main import app
from app.models import (
    Family,
    FamilyMember,
    FamilyParent,
    ParentAuthorization,
    ParentConsent,
    ParentProfile,
    User,
)


class ParentAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False)
        Base.metadata.create_all(self.engine)
        self.db = self.session_factory()

        self.user_a = self.create_user("family-a@example.com")
        self.user_b = self.create_user("family-b@example.com")
        self.unlinked_user = self.create_user("unlinked@example.com")
        self.parent_user = self.create_user("parent@example.com")
        self.family_a = Family(id="family-a", primary_user_id=self.user_a.id, name="Family A")
        self.family_b = Family(id="family-b", primary_user_id=self.user_b.id, name="Family B")
        self.db.add_all([self.family_a, self.family_b])
        self.db.flush()
        self.member_a = FamilyMember(id="member-a", family_id=self.family_a.id, user_id=self.user_a.id)
        self.member_b = FamilyMember(id="member-b", family_id=self.family_b.id, user_id=self.user_b.id)
        self.db.add_all([self.member_a, self.member_b])
        self.parent = ParentProfile(
            id="parent-a",
            parent_user_id=self.parent_user.id,
            full_name="Parent A",
            address_line1="123 Main Street",
            city="Pune",
            state="Maharashtra",
            postal_code="411001",
            preferred_language="English",
        )
        self.db.add(self.parent)
        self.db.flush()
        self.db.add_all([
            FamilyParent(
                id="family-parent-a",
                family_id=self.family_a.id,
                parent_id=self.parent.id,
                relationship_type="daughter",
            ),
            ParentAuthorization(
                id="authorization-a",
                parent_id=self.parent.id,
                family_member_id=self.member_a.id,
                can_edit_profile=True,
                can_manage_consent=True,
                can_view_visits=True,
            ),
            ParentConsent(
                id="personal-consent",
                parent_id=self.parent.id,
                status="active",
                consent_source="parent",
                scope="Existing parent consent",
                consent_text="The parent personally granted this consent.",
                signed_by_user_id=self.parent_user.id,
                effective_at=datetime.now(timezone.utc),
            ),
        ])
        self.db.commit()

        def override_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = lambda: self.current_user
        self.current_user = self.user_a
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_user(self, email: str) -> User:
        user = User(email=email, full_name=email.split("@", 1)[0])
        self.db.add(user)
        self.db.flush()
        return user

    def test_parent_data_isolation_between_families(self):
        response = self.client.get("/api/v1/carecircle/parents/parent-a")
        self.assertEqual(response.status_code, 200)

        self.current_user = self.user_b
        response = self.client.get("/api/v1/carecircle/parents/parent-a")
        self.assertEqual(response.status_code, 403)
        response = self.client.get("/api/v1/carecircle/parents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_family_members_require_parent_authorization(self):
        self.db.add(FamilyMember(
            id="member-without-parent-access",
            family_id=self.family_a.id,
            user_id=self.unlinked_user.id,
        ))
        self.db.commit()

        self.current_user = self.unlinked_user
        response = self.client.get("/api/v1/carecircle/parents/parent-a")
        self.assertEqual(response.status_code, 403)

    def test_family_report_is_not_personal_consent_or_a_replacement(self):
        response = self.client.post(
            "/api/v1/carecircle/parents/parent-a/consents",
            json={
                "scope": "Companionship visits",
                "consent_text": "The family member reports that the parent agreed.",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "family_reported")
        self.assertEqual(response.json()["consent_source"], "family_reported")
        self.assertIsNone(response.json()["effective_at"])

        self.db.expire_all()
        records = {
            consent.id: consent
            for consent in self.db.query(ParentConsent).filter(ParentConsent.parent_id == "parent-a").all()
        }
        self.assertEqual(records["personal-consent"].status, "active")
        self.assertEqual(response.json()["status"], "family_reported")

    def test_only_parent_can_withdraw_personal_consent(self):
        response = self.client.post(
            "/api/v1/carecircle/parents/parent-a/consents/personal-consent/withdraw",
            json={"reason": "Family member requested withdrawal"},
        )
        self.assertEqual(response.status_code, 403)

        self.current_user = self.parent_user
        response = self.client.post(
            "/api/v1/carecircle/parents/parent-a/consents/personal-consent/withdraw",
            json={"reason": "I changed my mind"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "withdrawn")

    def test_parent_personal_consent_is_only_active_for_parent_identity(self):
        self.current_user = self.parent_user
        response = self.client.post(
            "/api/v1/carecircle/parents/parent-a/consents",
            json={
                "scope": "Companionship visits",
                "consent_text": "I personally agree to companionship visits.",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "active")
        self.assertEqual(response.json()["consent_source"], "parent")

    def test_courier_supabase_access_token_authenticates_carecircle(self):
        app.dependency_overrides.pop(get_current_user)
        settings = Settings(
            _env_file=None,
            supabase_url="https://platform.example",
            supabase_anon_key="public-key",
            supabase_jwt_algorithm="HS256",
            supabase_jwt_secret="shared-platform-secret",
        )
        claims = {
            "sub": self.unlinked_user.id,
            "email": self.unlinked_user.email,
            "aud": "authenticated",
            "exp": int(time()) + 300,
            "iss": "https://platform.example/auth/v1",
            "user_metadata": {"full_name": "Shared User"},
        }
        token = jwt.encode(claims, settings.supabase_jwt_secret, algorithm="HS256")

        with patch("app.auth.get_settings", return_value=settings):
            response = self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.unlinked_user.id)
        self.assertEqual(response.json()["full_name"], "unlinked")
        self.assertEqual(
            self.db.query(FamilyMember).filter(FamilyMember.user_id == self.unlinked_user.id).count(),
            1,
        )


if __name__ == "__main__":
    unittest.main()
