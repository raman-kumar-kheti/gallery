from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.event import EventType, EventStatus
from app.services.event_service import EventService
from app.core.rbac import verify_event_access
from app.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()


class CreateEventRequest(BaseModel):
    title: str
    event_type: EventType = EventType.other
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class AddUploaderRequest(BaseModel):
    user_id: uuid.UUID
    expires_at: Optional[datetime] = None


@router.get("/")
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all events accessible to the current user."""
    service = EventService(db)
    events = await service.get_user_events(current_user)
    return {"events": [
        {
            "id": str(e.id),
            "title": e.title,
            "slug": e.slug,
            "event_type": e.event_type,
            "status": e.status,
            "image_count": e.image_count,
            "storage_used_bytes": e.storage_used_bytes,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    body: CreateEventRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new event."""
    service = EventService(db)
    event = await service.create_event(
        user=current_user,
        title=body.title,
        event_type=body.event_type,
        description=body.description,
        expires_at=body.expires_at,
    )
    return {
        "id": str(event.id),
        "title": event.title,
        "slug": event.slug,
        "status": event.status,
        "created_at": event.created_at.isoformat(),
    }


@router.get("/{event_id}")
async def get_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get event details."""
    service = EventService(db)
    event = await service.get_event_or_404(event_id)
    can_access = await verify_event_access(event, current_user, db)
    if not can_access:
        raise ForbiddenError("Access denied to this event")
    return {
        "id": str(event.id),
        "title": event.title,
        "slug": event.slug,
        "description": event.description,
        "event_type": event.event_type,
        "status": event.status,
        "image_count": event.image_count,
        "faiss_index_path": event.faiss_index_path,
        "index_version": event.index_version,
        "expires_at": event.expires_at.isoformat() if event.expires_at else None,
        "created_at": event.created_at.isoformat(),
    }


@router.patch("/{event_id}/activate")
async def activate_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    event = await service.get_event_or_404(event_id)
    can_access = await verify_event_access(event, current_user, db, require_write=True)
    if not can_access:
        raise ForbiddenError()
    event = await service.activate_event(event)
    return {"status": event.status}


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    event = await service.get_event_or_404(event_id)
    await service.delete_event(event, current_user)


@router.post("/{event_id}/uploaders")
async def add_event_uploader(
    event_id: uuid.UUID,
    body: AddUploaderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Grant temporary upload access to another user."""
    service = EventService(db)
    event = await service.get_event_or_404(event_id)
    can_access = await verify_event_access(event, current_user, db, require_write=True)
    if not can_access:
        raise ForbiddenError()
    await service.add_uploader(event, body.user_id, body.expires_at)
    return {"message": "Uploader added successfully"}
