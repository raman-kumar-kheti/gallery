from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.event import Event
from app.repositories.organization_repo import OrganizationRepository


# ──────────────────────────────────────────────────────────────
# Permission constants
# ──────────────────────────────────────────────────────────────
class Permissions:
    CREATE_EVENT = "create_event"
    UPLOAD_IMAGES = "upload_images"
    MANAGE_USERS = "manage_users"
    MANAGE_BILLING = "manage_billing"
    VIEW_ANALYTICS = "view_analytics"
    DELETE_EVENT = "delete_event"


# ──────────────────────────────────────────────────────────────
# Role → default permissions mapping (used for seeding)
# ──────────────────────────────────────────────────────────────
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "owner": [
        Permissions.CREATE_EVENT,
        Permissions.UPLOAD_IMAGES,
        Permissions.MANAGE_USERS,
        Permissions.MANAGE_BILLING,
        Permissions.VIEW_ANALYTICS,
        Permissions.DELETE_EVENT,
    ],
    "manager": [
        Permissions.CREATE_EVENT,
        Permissions.UPLOAD_IMAGES,
        Permissions.VIEW_ANALYTICS,
        Permissions.DELETE_EVENT,
    ],
    "uploader": [
        Permissions.UPLOAD_IMAGES,
    ],
}


# ──────────────────────────────────────────────────────────────
# RBAC dependency factory
# ──────────────────────────────────────────────────────────────
def require_permission(permission_key: str) -> Callable:
    """
    Returns a FastAPI dependency that checks if the current user
    has the given permission within their organization.
    """

    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        from app.repositories.organization_repo import OrganizationRepository

        org_repo = OrganizationRepository(db)
        has_perm = await org_repo.user_has_permission(
            user_id=current_user.id, permission_key=permission_key
        )
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{permission_key}' required",
            )
        return current_user

    return check_permission


# ──────────────────────────────────────────────────────────────
# Event ownership check utility
# ──────────────────────────────────────────────────────────────
async def verify_event_access(
    event: Event,
    current_user: User,
    db: AsyncSession,
    require_write: bool = False,
) -> bool:
    """
    Returns True if the user can access the event.
    For write access, checks ownership or org membership with upload permission.
    """
    # Direct ownership
    if event.owner_user_id and event.owner_user_id == current_user.id:
        return True

    # Org membership
    if event.organization_id:
        org_repo = OrganizationRepository(db)
        member = await org_repo.get_member(
            org_id=event.organization_id, user_id=current_user.id
        )
        if member:
            if not require_write:
                return True
            # Check upload permission for write access
            has_perm = await org_repo.user_has_permission(
                user_id=current_user.id, permission_key=Permissions.UPLOAD_IMAGES
            )
            return has_perm

    # Check if user is an event uploader
    from app.repositories.event_repo import EventRepository
    event_repo = EventRepository(db)
    is_uploader = await event_repo.is_event_uploader(
        event_id=event.id, user_id=current_user.id
    )
    return is_uploader
