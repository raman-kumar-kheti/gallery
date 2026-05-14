import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.image import Image, ProcessingStatus
from app.repositories.event_repo import EventRepository, ImageRepository
from app.services.storage_service import storage_service
from app.workers.celery_app import celery_app
from app.core.exceptions import NotFoundError, StorageQuotaExceededError


class UploadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = EventRepository(db)
        self.image_repo = ImageRepository(db)

    async def upload_image(
        self, event_id: uuid.UUID, file: UploadFile, uploader: User
    ) -> Image:
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundError("Event", str(event_id))

        # Read file content
        content = await file.read()
        file_size = len(content)
        mime_type = file.content_type or "image/jpeg"
        ext = mime_type.split("/")[-1].replace("jpeg", "jpg")

        # Create image record first to get UUID
        image = await self.image_repo.create(
            event_id=event_id,
            uploaded_by=uploader.id,
            image_url="",  # Filled after upload
            file_size=file_size,
            mime_type=mime_type,
            processing_status=ProcessingStatus.pending,
        )

        # Upload to R2
        key = storage_service.make_image_key(event_id, image.id, ext)
        import io
        image_url = storage_service.upload_file(
            io.BytesIO(content), key, content_type=mime_type
        )

        # Update record with URL
        image = await self.image_repo.update(image, image_url=image_url)

        # Update event storage and count
        await self.event_repo.increment_image_count(event_id)

        # Queue AI processing task
        celery_app.send_task(
            "worker.tasks.process_image.process_image_task",
            kwargs={
                "image_id": str(image.id),
                "event_id": str(event_id),
                "image_url": image_url,
            },
            queue="ai_processing",
        )

        return image

    async def generate_presigned_upload(
        self, event_id: uuid.UUID, filename: str, content_type: str
    ) -> dict:
        """Generate presigned URL for direct client-to-R2 upload."""
        image_id = uuid.uuid4()
        ext = content_type.split("/")[-1].replace("jpeg", "jpg")
        key = storage_service.make_image_key(event_id, image_id, ext)
        presigned = storage_service.generate_presigned_upload_url(key, content_type)
        return {
            "image_id": str(image_id),
            "upload_url": presigned["url"],
            "upload_fields": presigned["fields"],
            "key": key,
        }
