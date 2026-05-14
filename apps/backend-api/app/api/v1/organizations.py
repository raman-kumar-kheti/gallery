from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User, AccountType
from app.repositories.organization_repo import OrganizationRepository
from app.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()


class InviteMemberRequest(BaseModel):
    user_id: uuid.UUID
    role_name: str  # owner, manager, uploader


@router.get("/me")
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the organization for the current Studio user."""
    if current_user.account_type != AccountType.studio:
        raise HTTPException(status_code=403, detail="Only Studio accounts have organizations")

    org_repo = OrganizationRepository(db)
    org = await org_repo.get_by_owner(current_user.id)
    if not org:
        raise NotFoundError("Organization")

    return {
        "id": str(org.id),
        "name": org.name,
        "slug": org.slug,
        "storage_limit_bytes": org.storage_limit_bytes,
        "storage_used_bytes": org.storage_used_bytes,
        "created_at": org.created_at.isoformat(),
    }


@router.get("/me/members")
async def list_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all members of the current user's organization."""
    if current_user.account_type != AccountType.studio:
        raise HTTPException(status_code=403, detail="Only Studio accounts have organizations")

    org_repo = OrganizationRepository(db)
    org = await org_repo.get_by_owner(current_user.id)
    if not org:
        raise NotFoundError("Organization")

    members = await org_repo.get_members(org.id)
    return {"members": [
        {
            "id": str(m.id),
            "user_id": str(m.user_id),
            "user_name": m.user.name,
            "user_email": m.user.email,
            "role": m.role.name,
            "created_at": m.created_at.isoformat(),
        }
        for m in members
    ]}


@router.post("/me/members", status_code=status.HTTP_201_CREATED)
async def invite_member(
    body: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to the organization with a specific role."""
    if current_user.account_type != AccountType.studio:
        raise HTTPException(status_code=403, detail="Only Studio accounts support members")

    org_repo = OrganizationRepository(db)
    org = await org_repo.get_by_owner(current_user.id)
    if not org:
        raise NotFoundError("Organization")

    role = await org_repo.get_role_by_name(body.role_name)
    if not role:
        raise HTTPException(status_code=400, detail=f"Invalid role: {body.role_name}")

    # Check if already a member
    existing = await org_repo.get_member(org.id, body.user_id)
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member")

    member = await org_repo.add_member(org.id, body.user_id, role.id)
    return {"message": "Member added", "member_id": str(member.id)}


@router.delete("/me/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from the organization."""
    from sqlalchemy import select
    from app.models.organization import OrganizationMember

    if current_user.account_type != AccountType.studio:
        raise HTTPException(status_code=403, detail="Only Studio accounts support members")

    result = await db.execute(
        select(OrganizationMember).where(OrganizationMember.id == member_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise NotFoundError("Member", str(member_id))

    await db.delete(member)
    await db.flush()
