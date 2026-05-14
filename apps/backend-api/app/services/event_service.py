import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.models.event import Event, EventStatus, EventType
from app.models.user import User, AccountType
from app.repositories.event_repo import EventRepository
from app.repositories.organization_repo import OrganizationRepository
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.core.rbac import verify_event_access


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = EventRepository(db)
        self.org_repo = OrganizationRepository(db)

    async def create_event(
        self,
        user: User,
        title: str,
        event_type: EventType = EventType.other,
        description: str | None = None,
        expires_at=None,
    ) -> Event:
        slug = slugify(title)
        # Ensure slug uniqueness
        existing = await self.event_repo.get_by_slug(slug)
        if existing:
            slug = f"{slug}-{str(uuid.uuid4())[:8]}"

        # Determine owner vs org assignment
        org_id = None
        owner_id = user.id

        if user.account_type == AccountType.studio:
            # Studio events belong to org
            org = await self.org_repo.get_by_owner(user.id)
            if org:
                org_id = org.id
                owner_id = None

        event = await self.event_repo.create(
            title=title,
            slug=slug,
            description=description,
            event_type=event_type,
            status=EventStatus.draft,
            owner_user_id=owner_id,
            organization_id=org_id,
            expires_at=expires_at,
        )
        return event

    async def get_event_or_404(self, event_id: uuid.UUID) -> Event:
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundError("Event", str(event_id))
        return event

    async def get_user_events(self, user: User) -> list[Event]:
        if user.account_type == AccountType.studio:
            org = await self.org_repo.get_by_owner(user.id)
            if org:
                return await self.event_repo.list_by_organization(org.id)
        return await self.event_repo.list_by_owner(user.id)

    async def activate_event(self, event: Event) -> Event:
        return await self.event_repo.update(event, status=EventStatus.active)

    async def archive_event(self, event: Event) -> Event:
        return await self.event_repo.update(event, status=EventStatus.archived)

    async def delete_event(self, event: Event, user: User) -> None:
        can_access = await verify_event_access(event, user, self.db, require_write=True)
        if not can_access:
            raise ForbiddenError("You do not have permission to delete this event")
        await self.event_repo.delete(event)

    async def add_uploader(
        self, event: Event, invitee_user_id: uuid.UUID, expires_at=None
    ) -> None:
        from app.models.event import EventUploader
        uploader = EventUploader(
            event_id=event.id,
            user_id=invitee_user_id,
            expires_at=expires_at,
        )
        self.db.add(uploader)
        await self.db.flush()
