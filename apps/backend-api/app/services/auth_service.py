import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.config import settings
from app.repositories.user_repo import UserRepository
from app.repositories.organization_repo import OrganizationRepository
from app.models.user import User, AuthProvider, AccountType
from app.core.security import create_access_token, create_refresh_token


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_google_oauth_url(self) -> str:
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    async def exchange_google_code(self, code: str) -> dict:
        """Exchange OAuth code for Google access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        """Fetch user profile from Google."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    async def get_or_create_user(self, google_user_info: dict) -> tuple[User, bool]:
        """
        Returns (user, is_new_user).
        is_new_user=True when onboarding is required.
        """
        email = google_user_info["email"]
        provider_id = google_user_info["sub"]

        # Try to find by provider ID first
        user = await self.user_repo.get_by_provider_id(provider_id)
        if user:
            return user, False

        # Try by email
        user = await self.user_repo.get_by_email(email)
        if user:
            # Update provider ID if missing
            if not user.auth_provider_id:
                await self.user_repo.update(user, auth_provider_id=provider_id)
            return user, not user.onboarding_completed

        # Create new user
        user = await self.user_repo.create(
            email=email,
            name=google_user_info.get("name", email.split("@")[0]),
            avatar_url=google_user_info.get("picture"),
            auth_provider=AuthProvider.google,
            auth_provider_id=provider_id,
            onboarding_completed=False,
        )
        return user, True

    async def complete_onboarding(
        self, user: User, account_type: AccountType, org_name: Optional[str] = None
    ) -> User:
        """Complete user onboarding — set account type, create org if Studio."""
        await self.user_repo.update(
            user,
            account_type=account_type,
            onboarding_completed=True,
        )

        if account_type == AccountType.studio and org_name:
            from slugify import slugify
            org_repo = OrganizationRepository(self.db)
            slug = slugify(org_name)
            # Ensure unique slug
            existing = await org_repo.get_by_slug(slug)
            if existing:
                slug = f"{slug}-{str(user.id)[:8]}"

            org = await org_repo.create(
                owner_user_id=user.id,
                name=org_name,
                slug=slug,
            )
            # Add owner as member with owner role
            owner_role = await org_repo.get_role_by_name("owner")
            if owner_role:
                await org_repo.add_member(
                    org_id=org.id, user_id=user.id, role_id=owner_role.id
                )

        return user

    def generate_tokens(self, user: User) -> dict:
        return {
            "access_token": create_access_token(
                str(user.id),
                extra_data={"email": user.email, "account_type": user.account_type},
            ),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "bearer",
        }
