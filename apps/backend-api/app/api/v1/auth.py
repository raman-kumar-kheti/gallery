from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User, AccountType
from app.services.auth_service import AuthService
from app.core.security import verify_refresh_token, create_access_token

router = APIRouter()


class OnboardingRequest(BaseModel):
    account_type: AccountType
    organization_name: Optional[str] = None  # Required if account_type == studio


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    is_new_user: bool
    onboarding_completed: bool


@router.get("/google")
async def google_login():
    """Redirect to Google OAuth consent screen."""
    from app.config import settings
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback — exchange code for tokens."""
    auth_service = AuthService(db)

    # Exchange code for Google tokens
    token_data = await auth_service.exchange_google_code(code)
    user_info = await auth_service.get_google_user_info(token_data["access_token"])

    # Get or create user
    user, is_new = await auth_service.get_or_create_user(user_info)

    # Issue Gallery JWT tokens
    tokens = auth_service.generate_tokens(user)

    return {
        **tokens,
        "is_new_user": is_new,
        "onboarding_completed": user.onboarding_completed,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "account_type": user.account_type,
        },
    }


@router.post("/onboarding")
async def complete_onboarding(
    body: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete user onboarding — set account type, create org for studios."""
    if current_user.onboarding_completed:
        raise HTTPException(status_code=400, detail="Onboarding already completed")

    if body.account_type == AccountType.studio and not body.organization_name:
        raise HTTPException(
            status_code=422,
            detail="organization_name is required for Studio accounts",
        )

    auth_service = AuthService(db)
    user = await auth_service.complete_onboarding(
        current_user, body.account_type, body.organization_name
    )

    return {
        "message": "Onboarding completed",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "account_type": user.account_type,
            "onboarding_completed": user.onboarding_completed,
        },
    }


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Issue a new access token from a valid refresh token."""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    from app.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token(
        str(user.id),
        extra_data={"email": user.email, "account_type": user.account_type},
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "account_type": current_user.account_type,
        "onboarding_completed": current_user.onboarding_completed,
    }
