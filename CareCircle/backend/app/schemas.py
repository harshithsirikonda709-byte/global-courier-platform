from datetime import date, datetime, time, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationInfo, field_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    account_type: Literal["family", "companion", "parent"] = "family"

    @field_validator("full_name")
    @classmethod
    def strip_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    account_type: Literal["family", "companion", "parent"] = "family"
    is_admin: bool = False


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    user: UserResponse


class ConfirmationPending(BaseModel):
    confirmation_required: bool = True
    message: str
    user_id: Optional[str] = None
    email: EmailStr


class EmergencyContactInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    relationship: Optional[str] = Field(default=None, max_length=80)
    phone: str = Field(min_length=7, max_length=32)
    alternate_phone: Optional[str] = Field(default=None, max_length=32)
    is_primary: bool = False

    @field_validator("phone", "alternate_phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]):
        if value is None:
            return value
        value = value.strip()
        if not value:
            return None
        if not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone must contain only digits and phone formatting characters")
        return value


class ParentProfileBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(default=None, max_length=32)
    phone: Optional[str] = Field(default=None, max_length=32)
    alternate_phone: Optional[str] = Field(default=None, max_length=32)
    address_line1: str = Field(min_length=5, max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    postal_code: str = Field(min_length=3, max_length=20)
    country: str = Field(default="India", min_length=2, max_length=120)
    address_instructions: Optional[str] = Field(default=None, max_length=1000)
    preferred_language: str = Field(min_length=2, max_length=80)
    interests: Optional[str] = Field(default=None, max_length=2000)
    accessibility_preferences: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("full_name", "address_line1", "city", "state", "preferred_language")
    @classmethod
    def strip_required(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("phone", "alternate_phone")
    @classmethod
    def validate_optional_phone(cls, value: Optional[str]):
        if value is None:
            return value
        value = value.strip()
        if not value:
            return None
        if not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone must contain only digits and phone formatting characters")
        return value


class ParentCreateRequest(ParentProfileBase):
    emergency_contacts: list[EmergencyContactInput] = Field(default_factory=list)
    relationship: Optional[str] = Field(default=None, max_length=80)


class ParentUpdateRequest(ParentProfileBase):
    emergency_contacts: list[EmergencyContactInput] = Field(default_factory=list)


class EmergencyContactResponse(EmergencyContactInput):
    model_config = ConfigDict(from_attributes=True)

    id: str


class ConsentCreateRequest(BaseModel):
    consent_text: str = Field(min_length=10, max_length=4000)
    scope: str = Field(min_length=3, max_length=160)
    expires_at: Optional[datetime] = None


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    consent_source: str
    scope: str
    consent_text: str
    signer_relationship: Optional[str] = None
    effective_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    withdrawal_reason: Optional[str] = None


class WithdrawalRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class CompanionProfileInput(BaseModel):
    display_name: str = Field(min_length=2, max_length=160)
    bio: str = Field(min_length=20, max_length=2000)
    languages: list[str] = Field(min_length=1, max_length=10)
    service_area: str = Field(min_length=2, max_length=160)
    timezone_name: str = Field(default="Asia/Kolkata", min_length=3, max_length=80)
    identity_document_type: str = Field(min_length=2, max_length=80)

    @field_validator("display_name", "bio", "service_area", "timezone_name", "identity_document_type")
    @classmethod
    def strip_companion_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, value: list[str]) -> list[str]:
        languages = [language.strip() for language in value if language.strip()]
        if not languages:
            raise ValueError("At least one language is required")
        return list(dict.fromkeys(languages))


class CompanionProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    display_name: str
    bio: str
    languages: list[str]
    service_area: str
    timezone_name: str
    identity_document_type: str
    identity_status: str
    approval_status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AvailabilityInput(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, value: time, info: ValidationInfo) -> time:
        start_time = info.data.get("start_time")
        if start_time and value <= start_time:
            raise ValueError("Availability end time must be after start time")
        return value


class AvailabilityUpdateRequest(BaseModel):
    availability: list[AvailabilityInput] = Field(max_length=7)

    @field_validator("availability")
    @classmethod
    def validate_unique_days(cls, value: list[AvailabilityInput]) -> list[AvailabilityInput]:
        weekdays = [item.weekday for item in value]
        if len(weekdays) != len(set(weekdays)):
            raise ValueError("Only one availability window per weekday is supported")
        return value


class AvailabilityResponse(AvailabilityInput):
    model_config = ConfigDict(from_attributes=True)

    id: str


class CompanionReviewRequest(BaseModel):
    action: Literal["verify_identity", "reject_identity", "approve", "reject"]
    notes: Optional[str] = Field(default=None, max_length=1000)


class CompanionAdminResponse(CompanionProfileResponse):
    user_id: str
    email: EmailStr
    phone: Optional[str] = None


class VisitCreateRequest(BaseModel):
    parent_id: str
    scheduled_start: datetime
    duration_minutes: int = Field(ge=30, le=240, multiple_of=30)
    requirements: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("scheduled_start")
    @classmethod
    def require_future_timezone_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Scheduled start must include a timezone")
        if value.astimezone(timezone.utc) <= datetime.now(timezone.utc):
            raise ValueError("Visit must be scheduled in the future")
        return value.astimezone(timezone.utc)


class VisitActionRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=1000)


class VisitAssignmentRequest(BaseModel):
    companion_id: str


class ParentLinkRequest(BaseModel):
    parent_user_id: str


class VisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: str
    family_id: str
    booked_by_user_id: str
    companion_id: Optional[str] = None
    scheduled_start: datetime
    duration_minutes: int
    requirements: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    assigned_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ParentResponse(ParentProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    emergency_contacts: list[EmergencyContactResponse] = Field(default_factory=list)
    consents: list[ConsentResponse] = Field(default_factory=list)
