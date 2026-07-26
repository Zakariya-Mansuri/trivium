from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one letter and one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str | None
    learning_intensity: str
    notification_prefs: dict
    created_at: datetime


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    learning_intensity: str | None = None
    notification_prefs: dict | None = None

    @field_validator("learning_intensity")
    @classmethod
    def valid_intensity(cls, v):
        if v is not None and v not in ("light", "balanced", "intense"):
            raise ValueError("learning_intensity must be one of: light, balanced, intense")
        return v


class LLMConfigIn(BaseModel):
    provider: str = Field(max_length=30)
    model: str | None = Field(default=None, max_length=120)
    api_key: str = Field(min_length=8, max_length=500)


class LLMConfigOut(BaseModel):
    provider: str | None
    model: str | None
    key_hint: str | None  # last 4 chars only — the key itself is never returned
    source: str  # 'user' | 'server_default'
    active_label: str


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one letter and one digit")
        return v
