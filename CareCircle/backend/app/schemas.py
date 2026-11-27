from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=32)
    password: str = Field(min_length=8, max_length=128)

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


class ParentResponse(ParentProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    emergency_contacts: list[EmergencyContactResponse] = Field(default_factory=list)
    consents: list[ConsentResponse] = Field(default_factory=list)
