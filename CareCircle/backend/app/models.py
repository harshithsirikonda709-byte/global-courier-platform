import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


def uuid_string():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=uuid_string)
    email = Column(String(320), unique=True, nullable=False, index=True)
    phone = Column(String(32), unique=True, nullable=True)
    full_name = Column(String(160), nullable=False)
    password_hash = Column(String(255), nullable=False)
    account_status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    family_memberships = relationship("FamilyMember", back_populates="user")


class Family(Base):
    __tablename__ = "families"

    id = Column(String, primary_key=True, default=uuid_string)
    primary_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(160), nullable=False)
    account_status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    members = relationship("FamilyMember", back_populates="family")
    parent_links = relationship("FamilyParent", back_populates="family")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(String, primary_key=True, default=uuid_string)
    family_id = Column(String, ForeignKey("families.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String(32), nullable=False, default="owner")
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    family = relationship("Family", back_populates="members")
    user = relationship("User", back_populates="family_memberships")


class ParentProfile(Base):
    __tablename__ = "parent_profiles"

    id = Column(String, primary_key=True, default=uuid_string)
    parent_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    full_name = Column(String(160), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(32), nullable=True)
    phone = Column(String(32), nullable=True)
    alternate_phone = Column(String(32), nullable=True)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(120), nullable=False, default="India")
    address_instructions = Column(Text, nullable=True)
    preferred_language = Column(String(80), nullable=False)
    interests = Column(Text, nullable=True)
    accessibility_preferences = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    family_links = relationship("FamilyParent", back_populates="parent")
    consents = relationship("ParentConsent", back_populates="parent")
    emergency_contacts = relationship("EmergencyContact", back_populates="parent")
    authorizations = relationship("ParentAuthorization", back_populates="parent")


class FamilyParent(Base):
    __tablename__ = "family_parents"

    id = Column(String, primary_key=True, default=uuid_string)
    family_id = Column(String, ForeignKey("families.id"), nullable=False)
    parent_id = Column(String, ForeignKey("parent_profiles.id"), nullable=False)
    relationship_type = Column(String(80), nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    family = relationship("Family", back_populates="parent_links")
    parent = relationship("ParentProfile", back_populates="family_links")


class ParentAuthorization(Base):
    __tablename__ = "parent_authorizations"

    id = Column(String, primary_key=True, default=uuid_string)
    parent_id = Column(String, ForeignKey("parent_profiles.id"), nullable=False)
    family_member_id = Column(String, ForeignKey("family_members.id"), nullable=False)
    role = Column(String(32), nullable=False, default="booking_member")
    can_edit_profile = Column(Boolean, nullable=False, default=True)
    can_manage_consent = Column(Boolean, nullable=False, default=True)
    can_view_visits = Column(Boolean, nullable=False, default=True)
    status = Column(String(32), nullable=False, default="active")
    authorized_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    parent = relationship("ParentProfile", back_populates="authorizations")


class ParentConsent(Base):
    __tablename__ = "parent_consents"

    id = Column(String, primary_key=True, default=uuid_string)
    parent_id = Column(String, ForeignKey("parent_profiles.id"), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    scope = Column(String(160), nullable=False)
    consent_text = Column(Text, nullable=False)
    signed_by_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    signer_relationship = Column(String(80), nullable=True)
    effective_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    withdrawn_by_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    withdrawal_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    parent = relationship("ParentProfile", back_populates="consents")


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(String, primary_key=True, default=uuid_string)
    parent_id = Column(String, ForeignKey("parent_profiles.id"), nullable=False)
    full_name = Column(String(160), nullable=False)
    relationship_type = Column(String(80), nullable=True)
    phone = Column(String(32), nullable=False)
    alternate_phone = Column(String(32), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    parent = relationship("ParentProfile", back_populates="emergency_contacts")

    @property
    def relationship(self):
        return self.relationship_type


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String(80), nullable=False)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
