"""
Seed script — run once to bootstrap the database with:
- Default roles & permissions
- All three account types (Studio, Photographer, Customer)
- Individual Organizations, Subscription Plans, and Events for each user type
- Event uploaders and cached guest search sessions

Usage: python -m app.scripts.seed
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models import (
    User,
    Role,
    Permission,
    RolePermission,
    Organization,
    OrganizationMember,
    Plan,
    Subscription,
    Event,
    EventUploader,
    SearchSession,
)
from app.models.user import AccountType
from app.core.rbac import ROLE_PERMISSIONS, Permissions


async def seed():
    engine = create_async_engine(settings.database_url)
    async with async_sessionmaker(engine)() as session:
        # ──────────────────────────────────────────────────────────────
        # 1. Seed Permissions & Roles
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding Roles & Permissions...")
        perm_map: dict[str, Permission] = {}
        all_perms = set(p for perms in ROLE_PERMISSIONS.values() for p in perms)
        
        # Check existing permissions
        existing_perms_res = await session.execute(select(Permission))
        existing_perms = {p.key: p for p in existing_perms_res.scalars().all()}
        
        for key in all_perms:
            if key in existing_perms:
                perm_map[key] = existing_perms[key]
            else:
                perm = Permission(id=uuid.uuid4(), key=key)
                session.add(perm)
                perm_map[key] = perm
        
        # Check existing roles
        existing_roles_res = await session.execute(select(Role))
        existing_roles = {r.name: r for r in existing_roles_res.scalars().all()}
        role_map: dict[str, Role] = {}

        for role_name, perm_keys in ROLE_PERMISSIONS.items():
            if role_name in existing_roles:
                role = existing_roles[role_name]
            else:
                role = Role(id=uuid.uuid4(), name=role_name)
                session.add(role)
            role_map[role_name] = role

            # Flush to get IDs
            await session.flush()

            # Seed role-permission mapping
            for key in perm_keys:
                # Check if role-permission mapping already exists
                existing_rp_res = await session.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm_map[key].id
                    )
                )
                if not existing_rp_res.scalar_one_or_none():
                    rp = RolePermission(role_id=role.id, permission_id=perm_map[key].id)
                    session.add(rp)

        await session.flush()
        print("✅ Roles & Permissions configured.")

        # ──────────────────────────────────────────────────────────────
        # 2. Seed Standard Billing Plans
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding Billing Plans...")
        plans_data = [
            {
                "id": uuid.UUID("2d3c4b5a-6e7f-8a9b-0c1d-2e3f4a5b6c7d"),
                "name": "Pro",
                "storage_limit_bytes": 250 * 1024 * 1024 * 1024, # 250 GB
                "event_limit": None,
                "monthly_price": 2499.00,
                "is_active": True
            },
            {
                "id": uuid.UUID("3d4c5b6a-7e8f-9a0b-1c2d-3e4f5a6b7c8d"),
                "name": "Starter",
                "storage_limit_bytes": 50 * 1024 * 1024 * 1024, # 50 GB
                "event_limit": 10,
                "monthly_price": 999.00,
                "is_active": True
            },
            {
                "id": uuid.UUID("4d5c6b7a-8e9f-0a1b-2c3d-4e5f6a7b8c9d"),
                "name": "Studio",
                "storage_limit_bytes": 1000 * 1024 * 1024 * 1024, # 1 TB
                "event_limit": None,
                "monthly_price": 5999.00,
                "is_active": True
            }
        ]

        seeded_plans = {}
        for plan_info in plans_data:
            existing_plan_res = await session.execute(
                select(Plan).where(Plan.name == plan_info["name"])
            )
            existing_plan = existing_plan_res.scalar_one_or_none()
            if not existing_plan:
                plan = Plan(**plan_info)
                session.add(plan)
                seeded_plans[plan_info["name"]] = plan
            else:
                seeded_plans[plan_info["name"]] = existing_plan
        
        await session.flush()
        print("✅ Billing Plans configured.")

        # ──────────────────────────────────────────────────────────────
        # 3. Seed Users (Studio, Photographer, Customer)
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding All Types of Users...")
        
        # A. Studio Owner
        owner_id = uuid.UUID("e4a9e52c-bd48-4395-8854-3e970b991100")
        existing_owner_res = await session.execute(
            select(User).where(User.id == owner_id)
        )
        owner = existing_owner_res.scalar_one_or_none()
        if not owner:
            owner = User(
                id=owner_id,
                name="Arjun Sharma",
                email="arjun@majesticevents.com",
                account_type=AccountType.studio,
                onboarding_completed=True,
            )
            session.add(owner)

        # B. Photographer
        photographer_id = uuid.UUID("a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d")
        existing_photographer_res = await session.execute(
            select(User).where(User.id == photographer_id)
        )
        photographer = existing_photographer_res.scalar_one_or_none()
        if not photographer:
            photographer = User(
                id=photographer_id,
                name="Rohan Das",
                email="rohan.captures@gmail.com",
                account_type=AccountType.photographer,
                onboarding_completed=True,
            )
            session.add(photographer)

        # C. Customer
        customer_id = uuid.UUID("b1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6e")
        existing_customer_res = await session.execute(
            select(User).where(User.id == customer_id)
        )
        customer = existing_customer_res.scalar_one_or_none()
        if not customer:
            customer = User(
                id=customer_id,
                name="Priya Patel",
                email="priya@patelfamily.com",
                account_type=AccountType.customer,
                onboarding_completed=True,
            )
            session.add(customer)

        await session.flush()
        print("✅ Users configured.")

        # ──────────────────────────────────────────────────────────────
        # 4. Seed Organizations & Organization Members
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding Organizations...")
        
        # A. Studio Owner's Org
        studio_org_id = uuid.UUID("8b9e6f3d-55e1-45a1-aa88-0f04c053c891")
        existing_studio_org_res = await session.execute(
            select(Organization).where(Organization.id == studio_org_id)
        )
        studio_org = existing_studio_org_res.scalar_one_or_none()
        if not studio_org:
            studio_org = Organization(
                id=studio_org_id,
                owner_user_id=owner.id,
                name="Majestic Events Studio",
                slug="majestic-events",
                storage_limit_bytes=seeded_plans["Pro"].storage_limit_bytes,
                storage_used_bytes=12 * 1024 * 1024 * 1024, # 12 GB
            )
            session.add(studio_org)

        # B. Photographer's Org
        photo_org_id = uuid.UUID("7b9e6f3d-55e1-45a1-aa88-0f04c053c892")
        existing_photo_org_res = await session.execute(
            select(Organization).where(Organization.id == photo_org_id)
        )
        photo_org = existing_photo_org_res.scalar_one_or_none()
        if not photo_org:
            photo_org = Organization(
                id=photo_org_id,
                owner_user_id=photographer.id,
                name="Rohan Das Photography",
                slug="rohan-captures",
                storage_limit_bytes=seeded_plans["Starter"].storage_limit_bytes,
                storage_used_bytes=4 * 1024 * 1024 * 1024, # 4 GB
            )
            session.add(photo_org)

        # C. Customer's Org
        customer_org_id = uuid.UUID("6b9e6f3d-55e1-45a1-aa88-0f04c053c893")
        existing_customer_org_res = await session.execute(
            select(Organization).where(Organization.id == customer_org_id)
        )
        customer_org = existing_customer_org_res.scalar_one_or_none()
        if not customer_org:
            customer_org = Organization(
                id=customer_org_id,
                owner_user_id=customer.id,
                name="Patel Family Workspace",
                slug="patel-family",
                storage_limit_bytes=seeded_plans["Studio"].storage_limit_bytes,
                storage_used_bytes=45 * 1024 * 1024 * 1024, # 45 GB
            )
            session.add(customer_org)

        await session.flush()

        # Seed Member Roles for each workspace
        org_memberships = [
            (studio_org.id, owner.id, "owner"),
            (photo_org.id, photographer.id, "owner"),
            (customer_org.id, customer.id, "owner"),
        ]
        for org_id, user_id, role_name in org_memberships:
            existing_member_res = await session.execute(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id
                )
            )
            if not existing_member_res.scalar_one_or_none():
                member = OrganizationMember(
                    organization_id=org_id,
                    user_id=user_id,
                    role_id=role_map[role_name].id
                )
                session.add(member)

        print("✅ Organizations and members configured.")

        # ──────────────────────────────────────────────────────────────
        # 5. Seed Subscriptions for each Organization
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding Subscriptions...")
        
        subscriptions_data = [
            # Studio Subscription: Pro Plan
            {
                "id": uuid.UUID("f5e4d3c2-b1a0-9f8e-7d6c-5b4a3f2e1d0c"),
                "organization_id": studio_org.id,
                "plan_id": seeded_plans["Pro"].id,
                "status": "active",
                "razorpay_subscription_id": "sub_MajesticPro992",
            },
            # Photographer Subscription: Starter Plan
            {
                "id": uuid.UUID("e5e4d3c2-b1a0-9f8e-7d6c-5b4a3f2e1d0d"),
                "organization_id": photo_org.id,
                "plan_id": seeded_plans["Starter"].id,
                "status": "active",
                "razorpay_subscription_id": "sub_RohanStarter109",
            },
            # Customer Subscription: Studio Plan
            {
                "id": uuid.UUID("d5e4d3c2-b1a0-9f8e-7d6c-5b4a3f2e1d0e"),
                "organization_id": customer_org.id,
                "plan_id": seeded_plans["Studio"].id,
                "status": "active",
                "razorpay_subscription_id": "sub_PatelStudio007",
            }
        ]

        for sub_info in subscriptions_data:
            existing_sub_res = await session.execute(
                select(Subscription).where(Subscription.id == sub_info["id"])
            )
            if not existing_sub_res.scalar_one_or_none():
                sub = Subscription(
                    id=sub_info["id"],
                    organization_id=sub_info["organization_id"],
                    plan_id=sub_info["plan_id"],
                    status=sub_info["status"],
                    razorpay_subscription_id=sub_info["razorpay_subscription_id"],
                    starts_at=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                )
                session.add(sub)

        await session.flush()
        print("✅ Subscriptions configured.")

        # ──────────────────────────────────────────────────────────────
        # 6. Seed Events for each User / Organization Setup
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding Events...")
        
        events_data = [
            # Studio Event: Wedding Event
            {
                "id": uuid.UUID("90e9803d-815d-45db-b2aa-f3b1850119b9"),
                "organization_id": studio_org.id,
                "owner_user_id": None,
                "title": "Mehta & Malhotra Grand Wedding",
                "slug": "mehta-malhotra-wedding",
                "event_type": "wedding",
                "status": "active",
                "storage_used_bytes": 12 * 1024 * 1024 * 1024,
                "image_count": 2450,
                "faiss_index_path": "event_90e9803d-815d-45db-b2aa-f3b1850119b9.index",
                "index_version": 4,
            },
            # Photographer Event: Portrait Session
            {
                "id": uuid.UUID("80e9803d-815d-45db-b2aa-f3b1850119b8"),
                "organization_id": photo_org.id,
                "owner_user_id": None,
                "title": "Sunsets & Portraits Session",
                "slug": "sunsets-portraits-session",
                "event_type": "other",
                "status": "active",
                "storage_used_bytes": 4 * 1024 * 1024 * 1024,
                "image_count": 520,
                "faiss_index_path": "event_80e9803d-815d-45db-b2aa-f3b1850119b8.index",
                "index_version": 1,
            },
            # Customer Event: Family Jubilee
            {
                "id": uuid.UUID("70e9803d-815d-45db-b2aa-f3b1850119b7"),
                "organization_id": customer_org.id,
                "owner_user_id": None,
                "title": "Patel Family Silver Jubilee",
                "slug": "patel-family-jubilee",
                "event_type": "corporate",
                "status": "active",
                "storage_used_bytes": 45 * 1024 * 1024 * 1024,
                "image_count": 8900,
                "faiss_index_path": "event_70e9803d-815d-45db-b2aa-f3b1850119b7.index",
                "index_version": 12,
            }
        ]

        seeded_events = {}
        for event_info in events_data:
            existing_event_res = await session.execute(
                select(Event).where(Event.id == event_info["id"])
            )
            existing_event = existing_event_res.scalar_one_or_none()
            if not existing_event:
                event = Event(
                    id=event_info["id"],
                    organization_id=event_info["organization_id"],
                    owner_user_id=event_info["owner_user_id"],
                    title=event_info["title"],
                    slug=event_info["slug"],
                    event_type=event_info["event_type"],
                    status=event_info["status"],
                    storage_used_bytes=event_info["storage_used_bytes"],
                    image_count=event_info["image_count"],
                    faiss_index_path=event_info["faiss_index_path"],
                    index_version=event_info["index_version"],
                    expires_at=datetime.now(timezone.utc) + timedelta(days=90)
                )
                session.add(event)
                seeded_events[event_info["id"]] = event
            else:
                seeded_events[event_info["id"]] = existing_event

        await session.flush()
        print("✅ Events configured.")

        # ──────────────────────────────────────────────────────────────
        # 7. Seed Cross-Invitations / Event Uploaders
        # ──────────────────────────────────────────────────────────────
        # Link Photographer as an Event Uploader on Studio's Wedding Event
        existing_uploader_res = await session.execute(
            select(EventUploader).where(
                EventUploader.event_id == uuid.UUID("90e9803d-815d-45db-b2aa-f3b1850119b9"),
                EventUploader.user_id == photographer.id
            )
        )
        if not existing_uploader_res.scalar_one_or_none():
            uploader = EventUploader(
                event_id=uuid.UUID("90e9803d-815d-45db-b2aa-f3b1850119b9"),
                user_id=photographer.id,
                permissions="upload_images",
                expires_at=datetime.now(timezone.utc) + timedelta(days=2)
            )
            session.add(uploader)

        # ──────────────────────────────────────────────────────────────
        # 8. Seed Guest Search Session for wedding
        # ──────────────────────────────────────────────────────────────
        print("🌱 Seeding Guest Search Session...")
        session_id = uuid.UUID("ff99aa88-bb77-cc66-dd55-ee44ff33bb22")
        existing_session_res = await session.execute(
            select(SearchSession).where(SearchSession.id == session_id)
        )
        if not existing_session_res.scalar_one_or_none():
            search_session = SearchSession(
                id=session_id,
                event_id=uuid.UUID("90e9803d-815d-45db-b2aa-f3b1850119b9"),
                session_token="ss_tok_99182ab38cdef1092a3b839",
                query_image_url="https://storage.gallery.app/selfies/wedding_guest_selfie.jpg",
                matched_image_ids=[
                    "img_001d2e3f-4a5b-6c7d-8e9f-0a1b2c3d4e5f",
                    "img_7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
                    "img_ffeeddcc-bbaa-9988-7766-554433221100"
                ],
                index_version=4,
                expires_at=datetime.now(timezone.utc) + timedelta(days=1)
            )
            session.add(search_session)

        await session.commit()
        print("🚀 Database Seed completed successfully for all user types, plans, subscriptions, and events!")


if __name__ == "__main__":
    asyncio.run(seed())
