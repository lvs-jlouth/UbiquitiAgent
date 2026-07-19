"""Authentication schemas."""
from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    """Login request payload."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """Authenticated user information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr | str
    role: str
    is_active: bool
