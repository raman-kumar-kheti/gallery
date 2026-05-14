from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services.upload_service import UploadService
from app.repositories.event_repo import ImageRepository, EventRepository
from app.core.rbac import verify_event_access
from app.core.exceptions import ForbiddenError, NotFoundError

router = APIRouter()


@router.post("/upload/{event_id}")
async def upload_image(
    event_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a photo to an event. Queues AI processing automatically."""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/webp"]:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, WebP images are supported")

    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("Event", str(event_id))

    can_upload = await verify_event_access(event, current_user, db, require_write=True)
    if not can_upload:
        raise ForbiddenError("Upload permission required")

    service = UploadService(db)
    image = await service.upload_image(event_id, file, current_user)
    return {
        "id": str(image.id),
        "image_url": image.image_url,
        "processing_status": image.processing_status,
        "created_at": image.created_at.isoformat(),
    }


@router.get("/presigned-upload/{event_id}")
async def get_presigned_upload_url(
    event_id: uuid.UUID,
    filename: str,
    content_type: str = "image/jpeg",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a presigned URL for direct client-to-R2 upload (large files)."""
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("Event", str(event_id))

    can_upload = await verify_event_access(event, current_user, db, require_write=True)
    if not can_upload:
        raise ForbiddenError()

    service = UploadService(db)
    return await service.generate_presigned_upload(event_id, filename, content_type)


@router.get("/event/{event_id}")
async def list_event_images(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all images in an event."""
    event_repo = EventRepository(db)
    image_repo = ImageRepository(db)
    event = await event_repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("Event", str(event_id))

    can_access = await verify_event_access(event, current_user, db)
    if not can_access:
        raise ForbiddenError()

    images = await image_repo.list_by_event(event_id)
    return {"images": [
        {
            "id": str(img.id),
            "image_url": img.image_url,
            "thumbnail_url": img.thumbnail_url,
            "processing_status": img.processing_status,
            "width": img.width,
            "height": img.height,
            "file_size": img.file_size,
            "created_at": img.created_at.isoformat(),
        }
        for img in images
    ]}


@router.get("/{image_id}/status")
async def get_image_status(
    image_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check AI processing status of an image."""
    image_repo = ImageRepository(db)
    image = await image_repo.get_by_id(image_id)
    if not image:
        raise NotFoundError("Image", str(image_id))
    return {
        "id": str(image.id),
        "processing_status": image.processing_status,
        "faiss_pos": image.faiss_pos,
        "thumbnail_url": image.thumbnail_url,
    }
