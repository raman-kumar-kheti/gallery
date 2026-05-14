from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import secrets
import io
import qrcode
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.qr_code import QRCode
from app.models.event import Event
from app.repositories.event_repo import EventRepository
from app.core.rbac import verify_event_access
from app.core.exceptions import NotFoundError, ForbiddenError
from app.config import settings

router = APIRouter()


@router.post("/generate/{event_id}")
async def generate_qr_code(
    event_id: uuid.UUID,
    expires_days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a QR code for an event. Returns QR image URL and token."""
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("Event", str(event_id))

    can_access = await verify_event_access(event, current_user, db, require_write=True)
    if not can_access:
        raise ForbiddenError()

    # Create QR record
    token = secrets.token_urlsafe(16)
    qr_record = QRCode(
        event_id=event_id,
        qr_token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=expires_days),
    )
    db.add(qr_record)
    await db.flush()

    guest_url = f"{settings.app_url}/g/{token}"

    return {
        "id": str(qr_record.id),
        "qr_token": token,
        "guest_url": guest_url,
        "expires_at": qr_record.expires_at.isoformat(),
    }


@router.get("/image/{event_id}")
async def get_qr_image(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the QR code as a PNG image for download/display."""
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("Event", str(event_id))

    can_access = await verify_event_access(event, current_user, db)
    if not can_access:
        raise ForbiddenError()

    # Get latest QR code for this event
    result = await db.execute(
        select(QRCode)
        .where(QRCode.event_id == event_id)
        .order_by(QRCode.created_at.desc())
        .limit(1)
    )
    qr_record = result.scalar_one_or_none()
    if not qr_record:
        raise HTTPException(status_code=404, detail="No QR code found. Generate one first.")

    guest_url = f"{settings.app_url}/g/{qr_record.qr_token}"

    # Generate QR image in memory
    qr_img = qrcode.make(guest_url)
    img_bytes = io.BytesIO()
    qr_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")


@router.get("/resolve/{qr_token}")
async def resolve_qr_token(
    qr_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Guest endpoint: resolve QR token → event details.
    No auth required.
    """
    result = await db.execute(
        select(QRCode)
        .where(QRCode.qr_token == qr_token)
    )
    qr_record = result.scalar_one_or_none()
    if not qr_record:
        raise HTTPException(status_code=404, detail="Invalid QR code")

    # Check expiry
    if qr_record.expires_at and qr_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="QR code has expired")

    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(qr_record.event_id)
    if not event or event.status != "active":
        raise HTTPException(status_code=404, detail="Event not found or not active")

    return {
        "event_id": str(event.id),
        "event_title": event.title,
        "event_type": event.event_type,
    }
