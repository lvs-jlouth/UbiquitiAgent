"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.schemas.common import MessageResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Authenticate and obtain a token")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    service = UserService(db)
    user = await service.authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    await service.update_last_login(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse, summary="Log out")
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Stateless logout endpoint (client discards the token)."""
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserInfo, summary="Get current user")
async def me(current_user: User = Depends(get_current_active_user)) -> UserInfo:
    """Return the currently authenticated user's information."""
    return UserInfo.model_validate(current_user)
