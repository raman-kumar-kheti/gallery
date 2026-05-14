from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from app.models.event import Event, EventUploader
from app.models.image import Image


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, event_id: uuid.UUID) -> Optional[Event]:
        result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Event]:
        result = await self.db.execute(
            select(Event).where(Event.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_user_id: uuid.UUID) -> list[Event]:
        result = await self.db.execute(
            select(Event).where(Event.owner_user_id == owner_user_id)
            .order_by(Event.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_organization(self, org_id: uuid.UUID) -> list[Event]:
        result = await self.db.execute(
            select(Event).where(Event.organization_id == org_id)
            .order_by(Event.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Event:
        event = Event(**kwargs)
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def update(self, event: Event, **kwargs) -> Event:
        for key, value in kwargs.items():
            setattr(event, key, value)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def delete(self, event: Event) -> None:
        await self.db.delete(event)
        await self.db.flush()

    async def is_event_uploader(
        self, event_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        from datetime import datetime, timezone
        result = await self.db.execute(
            select(EventUploader).where(
                and_(
                    EventUploader.event_id == event_id,
                    EventUploader.user_id == user_id,
                    # Check not expired
                    (EventUploader.expires_at == None)
                    | (EventUploader.expires_at > datetime.now(timezone.utc)),
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def increment_image_count(self, event_id: uuid.UUID, count: int = 1) -> None:
        event = await self.get_by_id(event_id)
        if event:
            event.image_count += count
            await self.db.flush()

    async def update_faiss_path(self, event_id: uuid.UUID, path: str, version: int) -> None:
        event = await self.get_by_id(event_id)
        if event:
            event.faiss_index_path = path
            event.index_version = version
            await self.db.flush()


class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, image_id: uuid.UUID) -> Optional[Image]:
        result = await self.db.execute(
            select(Image).where(Image.id == image_id)
        )
        return result.scalar_one_or_none()

    async def list_by_event(self, event_id: uuid.UUID) -> list[Image]:
        result = await self.db.execute(
            select(Image).where(Image.event_id == event_id)
            .order_by(Image.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_faiss_positions(
        self, event_id: uuid.UUID, faiss_positions: list[int]
    ) -> list[Image]:
        """Map FAISS vector positions back to image rows."""
        result = await self.db.execute(
            select(Image).where(
                and_(
                    Image.event_id == event_id,
                    Image.faiss_pos.in_(faiss_positions),
                )
            )
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Image:
        image = Image(**kwargs)
        self.db.add(image)
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def update(self, image: Image, **kwargs) -> Image:
        for key, value in kwargs.items():
            setattr(image, key, value)
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def get_next_faiss_pos(self, event_id: uuid.UUID) -> int:
        """Get next available FAISS position for this event."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(Image.id)).where(
                and_(Image.event_id == event_id, Image.faiss_pos != None)
            )
        )
        return result.scalar_one() or 0
