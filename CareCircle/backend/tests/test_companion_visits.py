import unittest
from datetime import datetime, time, timedelta, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user, provision_family_user
from app.config import Settings
from app.database import Base, get_db
from app.main import app
from app.models import (
    CompanionAvailability,
    CompanionProfile,
    Family,
    FamilyMember,
    FamilyParent,
    ParentAuthorization,
    ParentConsent,
    ParentProfile,
    User,
    Visit,
)


class CompanionVisitTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False)
        Base.metadata.create_all(self.engine)
        self.db = self.session_factory()

        self.family_user = self.create_user("family@example.com")
        self.other_family_user = self.create_user("other@example.com")
        self.parent_user = self.create_user("parent@example.com", account_type="parent")
        self.companion_user = self.create_user("companion@example.com", account_type="companion")
        self.admin_user = self.create_user("admin@example.com")
        self.family = Family(id="family", primary_user_id=self.family_user.id, name="Family")
        self.other_family = Family(id="other-family", primary_user_id=self.other_family_user.id, name="Other")
        self.db.add_all([self.family, self.other_family])
        self.db.flush()
        self.family_member = FamilyMember(id="family-member", family_id=self.family.id, user_id=self.family_user.id)
        self.other_member = FamilyMember(id="other-member", family_id=self.other_family.id, user_id=self.other_family_user.id)
        self.db.add_all([self.family_member, self.other_member])
        self.parent = ParentProfile(
            id="parent",
            parent_user_id=self.parent_user.id,
            full_name="Parent Person",
            address_line1="123 Main Street",
            city="Pune",
            state="Maharashtra",
            postal_code="411001",
            preferred_language="English",
        )
        self.db.add(self.parent)
        self.db.flush()
        self.db.add_all([
            FamilyParent(id="family-parent", family_id=self.family.id, parent_id=self.parent.id),
            ParentAuthorization(
                id="parent-auth",
                parent_id=self.parent.id,
                family_member_id=self.family_member.id,
                can_edit_profile=True,
                can_manage_consent=True,
                can_view_visits=True,
            ),
            ParentConsent(
                id="parent-consent",
                parent_id=self.parent.id,
                status="active",
                consent_source="parent",
                scope="Companionship visits",
                consent_text="I personally agree to companionship visits.",
                signed_by_user_id=self.parent_user.id,
                effective_at=datetime.now(timezone.utc),
            ),
        ])
        self.companion = CompanionProfile(
            id="companion-profile",
            user_id=self.companion_user.id,
            display_name="Companion",
            bio="I enjoy conversation and local walks.",
            languages=["English"],
            service_area="Pune",
            timezone_name="Asia/Kolkata",
            identity_document_type="Government photo ID",
            identity_status="pending",
            approval_status="pending",
        )
        self.db.add(self.companion)
        self.db.commit()

        def override_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = lambda: self.current_user
        self.current_user = self.family_user
        self.client = TestClient(app)
        self.admin_settings = Settings(_env_file=None, admin_user_ids=[self.admin_user.id])

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_user(self, email: str, account_type: str = "family") -> User:
        user = User(email=email, full_name=email.split("@", 1)[0], account_type=account_type)
        self.db.add(user)
        self.db.flush()
        return user

    def create_visit(self) -> Visit:
        local_start = datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(days=14)
        local_start = local_start.replace(hour=10, minute=0, second=0, microsecond=0)
        self.db.add(CompanionAvailability(
            companion_id=self.companion.id,
            weekday=local_start.weekday(),
            start_time=time(0, 0),
            end_time=time(23, 59),
        ))
        self.db.commit()
        response = self.client.post(
            "/api/v1/carecircle/visits",
            json={
                "parent_id": self.parent.id,
                "scheduled_start": local_start.isoformat(),
                "duration_minutes": 60,
                "requirements": "Conversation and board games",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        visit_id = response.json()["id"]
        return self.db.query(Visit).filter(Visit.id == visit_id).one()

    def admin(self, method: str, path: str, **kwargs):
        self.current_user = self.admin_user
        with patch("app.auth.get_settings", return_value=self.admin_settings):
            return self.client.request(method, path, **kwargs)

    def test_companion_signup_does_not_create_family_membership(self):
        companion = provision_family_user(
            self.db,
            user_id="new-companion-id",
            email="new-companion@example.com",
            full_name="New Companion",
            account_type="companion",
        )
        self.assertEqual(companion.account_type, "companion")
        self.assertEqual(self.db.query(FamilyMember).filter(FamilyMember.user_id == companion.id).count(), 0)
        self.assertIsNotNone(self.db.query(CompanionProfile).filter(CompanionProfile.user_id == companion.id).first())

    def test_companion_account_cannot_use_family_profile_endpoint(self):
        self.current_user = self.companion_user
        response = self.client.get("/api/v1/carecircle/parents")
        self.assertEqual(response.status_code, 403)

    def test_companion_profile_and_availability_are_self_managed_but_not_approval(self):
        self.current_user = self.companion_user
        profile_response = self.client.put(
            "/api/v1/carecircle/companions/me",
            json={
                "display_name": "Companion One",
                "bio": "I enjoy conversation, reading, and local walks.",
                "languages": ["English", "Marathi"],
                "service_area": "Pune",
                "timezone_name": "Asia/Kolkata",
                "identity_document_type": "Government photo ID",
                "approval_status": "approved",
                "identity_status": "verified",
            },
        )
        self.assertEqual(profile_response.status_code, 200, profile_response.text)
        self.assertEqual(profile_response.json()["identity_status"], "pending")
        self.assertEqual(profile_response.json()["approval_status"], "pending")

        schedule_response = self.client.put(
            "/api/v1/carecircle/companions/me/availability",
            json={"availability": [
                {"weekday": 1, "start_time": "09:00", "end_time": "17:00"},
                {"weekday": 4, "start_time": "10:00", "end_time": "18:00"},
            ]},
        )
        self.assertEqual(schedule_response.status_code, 200, schedule_response.text)
        self.assertEqual(len(schedule_response.json()), 2)

    def test_admin_must_verify_identity_before_approval(self):
        denied = self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "approve"},
        )
        self.assertEqual(denied.status_code, 409)
        verified = self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "verify_identity", "notes": "Document reviewed"},
        )
        self.assertEqual(verified.status_code, 200, verified.text)
        approved = self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "approve"},
        )
        self.assertEqual(approved.status_code, 200, approved.text)
        self.assertEqual(approved.json()["approval_status"], "approved")

    def test_unverified_companion_cannot_be_assigned(self):
        visit = self.create_visit()
        response = self.admin(
            "POST",
            f"/api/v1/carecircle/admin/visits/{visit.id}/assign",
            json={"companion_id": self.companion.id},
        )
        self.assertEqual(response.status_code, 409)

    def test_assignment_requires_companion_availability(self):
        visit = self.create_visit()
        self.db.query(CompanionAvailability).filter(
            CompanionAvailability.companion_id == self.companion.id,
        ).delete()
        self.db.commit()
        self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "verify_identity"},
        )
        self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "approve"},
        )
        response = self.admin(
            "POST",
            f"/api/v1/carecircle/admin/visits/{visit.id}/assign",
            json={"companion_id": self.companion.id},
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("not available", response.json()["detail"])

    def test_visit_requires_personal_parent_consent_and_is_family_isolated(self):
        self.db.query(ParentConsent).filter(ParentConsent.id == "parent-consent").update({
            "status": "family_reported",
            "consent_source": "family_reported",
        })
        self.db.commit()
        local_start = datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(days=14)
        response = self.client.post(
            "/api/v1/carecircle/visits",
            json={
                "parent_id": self.parent.id,
                "scheduled_start": local_start.isoformat(),
                "duration_minutes": 60,
            },
        )
        self.assertEqual(response.status_code, 409)

        self.db.query(ParentConsent).filter(ParentConsent.id == "parent-consent").update({"status": "withdrawn"})
        self.db.commit()
        response = self.client.post(
            "/api/v1/carecircle/visits",
            json={
                "parent_id": self.parent.id,
                "scheduled_start": local_start.isoformat(),
                "duration_minutes": 60,
            },
        )
        self.assertEqual(response.status_code, 409)

        self.db.query(ParentConsent).filter(ParentConsent.id == "parent-consent").update({
            "status": "active",
            "consent_source": "parent",
        })
        self.db.commit()
        visit = self.create_visit()
        self.current_user = self.other_family_user
        self.assertEqual(self.client.get("/api/v1/carecircle/visits").json(), [])
        response = self.client.post(
            f"/api/v1/carecircle/visits/{visit.id}/cancel",
            json={"reason": "Not my visit"},
        )
        self.assertEqual(response.status_code, 403)

    def test_parent_consent_withdrawal_cancels_pending_scheduled_visits(self):
        visit = self.create_visit()
        self.current_user = self.parent_user
        response = self.client.post(
            f"/api/v1/carecircle/parents/{self.parent.id}/consents/parent-consent/withdraw",
            json={"reason": "I no longer want companionship visits"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.db.expire_all()
        saved_visit = self.db.query(Visit).filter(Visit.id == visit.id).one()
        self.assertEqual(saved_visit.status, "cancelled")
        self.assertEqual(saved_visit.cancellation_reason, "Parent withdrew personal consent")

    def test_full_visit_lifecycle_and_consent_gate(self):
        visit = self.create_visit()
        self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "verify_identity"},
        )
        self.admin(
            "POST",
            f"/api/v1/carecircle/admin/companions/{self.companion.id}/review",
            json={"action": "approve"},
        )
        assigned = self.admin(
            "POST",
            f"/api/v1/carecircle/admin/visits/{visit.id}/assign",
            json={"companion_id": self.companion.id},
        )
        self.assertEqual(assigned.status_code, 200, assigned.text)
        self.assertEqual(assigned.json()["status"], "assigned")

        self.current_user = self.companion_user
        accepted = self.client.post(f"/api/v1/carecircle/visits/{visit.id}/accept", json={})
        self.assertEqual(accepted.status_code, 200, accepted.text)
        self.assertEqual(accepted.json()["status"], "accepted")

        self.db.query(ParentConsent).filter(ParentConsent.id == "parent-consent").update({"status": "withdrawn"})
        self.db.commit()
        check_in = self.client.post(f"/api/v1/carecircle/visits/{visit.id}/check-in")
        self.assertEqual(check_in.status_code, 409)

        self.db.query(ParentConsent).filter(ParentConsent.id == "parent-consent").update({"status": "active"})
        self.db.commit()
        check_in = self.client.post(f"/api/v1/carecircle/visits/{visit.id}/check-in")
        self.assertEqual(check_in.status_code, 200, check_in.text)
        completed = self.client.post(f"/api/v1/carecircle/visits/{visit.id}/check-out")
        self.assertEqual(completed.status_code, 200, completed.text)
        self.assertEqual(completed.json()["status"], "completed")
        self.assertTrue(completed.json()["checked_in_at"])
        self.assertTrue(completed.json()["checked_out_at"])

    def test_non_admin_cannot_review_or_assign(self):
        response = self.client.get("/api/v1/carecircle/admin/companions")
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
