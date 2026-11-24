from datetime import datetime

from pydantic import BaseModel, Field


class CustomerProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    address_line_1: str | None = Field(default=None, max_length=200)
    address_line_2: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str = Field(default="India", max_length=100)


class CustomerProfile(CustomerProfileUpdate):
    user_id: str
    email: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

