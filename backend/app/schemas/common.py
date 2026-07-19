"""Common shared schemas."""
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic message response."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    model_config = ConfigDict(from_attributes=True)

    error: str
    detail: str | None = None
    code: int | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response container."""

    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    total: int
    skip: int
    limit: int
