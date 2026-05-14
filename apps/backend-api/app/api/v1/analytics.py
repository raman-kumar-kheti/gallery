"""
Analytics / admin routes — internal use only.
Provides event-level stats and audit log access.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.image import Image, ProcessingStatus
from app.models.audit_log import AuditLog
from app.repositories.event_repo import EventRepository
from app.core.rbac import verify_event_access
from app.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()


@router.get("/events/{event_id}/stats")
async def get_event_stats(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return processing stats for all images in an event."""
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("Event", str(event_id))

    can_access = await verify_event_access(event, current_user, db)
    if not can_access:
        raise ForbiddenError()

    # Count images by processing status
    result = await db.execute(
        select(Image.processing_status, func.count(Image.id))
        .where(Image.event_id == event_id)
        .group_by(Image.processing_status)
    )
    status_counts = {row[0].value: row[1] for row in result.fetchall()}

    # Count indexed images (have faiss_pos)
    indexed_result = await db.execute(
        select(func.count(Image.id)).where(
            Image.event_id == event_id,
            Image.faiss_pos.isnot(None),
        )
    )
    indexed_count = indexed_result.scalar_one()

    return {
        "event_id": str(event_id),
        "image_count": event.image_count,
        "indexed_count": indexed_count,
        "index_version": event.index_version,
        "by_status": status_counts,
        "storage_used_bytes": event.storage_used_bytes,
        "faiss_index_path": event.faiss_index_path,
    }


@router.get("/audit-logs")
async def list_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List recent audit logs for the current user."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    return {"logs": [
        {
            "id": str(log.id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "metadata": log.metadata,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]}
