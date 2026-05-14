"""
Seed script — run once after initial migration to bootstrap roles and permissions.
Usage: python -m app.scripts.seed

NOTE: The initial migration (001) already seeds roles and permissions via bulk_insert.
This script is a standalone utility for re-seeding a clean database outside of Alembic.
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.models.role import Role, Permission, RolePermission
from app.core.rbac import ROLE_PERMISSIONS


async def seed():
    engine = create_async_engine(settings.database_url)
    async with async_sessionmaker(engine)() as session:
        # Create permissions
        perm_map: dict[str, Permission] = {}
        all_perms = set(p for perms in ROLE_PERMISSIONS.values() for p in perms)
        for key in all_perms:
            perm = Permission(id=uuid.uuid4(), key=key)
            session.add(perm)
            perm_map[key] = perm

        # Create roles + link permissions
        for role_name, perm_keys in ROLE_PERMISSIONS.items():
            role = Role(id=uuid.uuid4(), name=role_name)
            session.add(role)
            for key in perm_keys:
                rp = RolePermission(role_id=role.id, permission_id=perm_map[key].id)
                session.add(rp)

        await session.commit()
        print(f"✅ Seeded {len(all_perms)} permissions and {len(ROLE_PERMISSIONS)} roles.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
