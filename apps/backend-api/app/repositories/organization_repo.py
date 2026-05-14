from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from app.models.organization import Organization, OrganizationMember
from app.models.role import Role, Permission, RolePermission


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        result = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_user_id: uuid.UUID) -> Optional[Organization]:
        result = await self.db.execute(
            select(Organization).where(Organization.owner_user_id == owner_user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Organization:
        org = Organization(**kwargs)
        self.db.add(org)
        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def get_member(
        self, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[OrganizationMember]:
        result = await self.db.execute(
            select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def add_member(
        self, org_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID
    ) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role_id=role_id,
        )
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    async def user_has_permission(
        self, user_id: uuid.UUID, permission_key: str
    ) -> bool:
        """Check if a user has a permission via their org role."""
        result = await self.db.execute(
            select(OrganizationMember)
            .join(Role, OrganizationMember.role_id == Role.id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(
                and_(
                    OrganizationMember.user_id == user_id,
                    Permission.key == permission_key,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_members(self, org_id: uuid.UUID) -> list[OrganizationMember]:
        result = await self.db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
            .options(selectinload(OrganizationMember.user), selectinload(OrganizationMember.role))
        )
        return list(result.scalars().all())

    async def increment_storage(self, org_id: uuid.UUID, bytes_added: int) -> None:
        org = await self.get_by_id(org_id)
        if org:
            org.storage_used_bytes += bytes_added
            await self.db.flush()
