import uuid
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.event_repo import EventRepository, ImageRepository
from app.repositories.search_session_repo import SearchSessionRepository
from app.services.storage_service import storage_service
from app.core.exceptions import NotFoundError
from app.workers.celery_app import celery_app


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = EventRepository(db)
        self.image_repo = ImageRepository(db)
        self.session_repo = SearchSessionRepository(db)

    async def search_by_selfie(
        self,
        event_id: uuid.UUID,
        selfie_file: UploadFile,
        session_token: str | None = None,
    ) -> dict:
        """
        Full guest search pipeline:
        1. Check cached session if token provided
        2. Upload selfie to R2
        3. Send to AI worker for embedding + FAISS search
        4. Return matching images
        """
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundError("Event", str(event_id))

        # Check cache
        if session_token:
            cached = await self.session_repo.get_by_token(session_token)
            if cached and await self.session_repo.is_cache_valid(cached, event.index_version):
                # Return cached results
                if cached.matched_image_ids:
                    images = await self.image_repo.get_by_faiss_positions(
                        event_id, cached.matched_image_ids
                    )
                    return {
                        "session_token": session_token,
                        "from_cache": True,
                        "images": images,
                    }

        # Upload selfie
        content = await selfie_file.read()
        session_id = uuid.uuid4()
        selfie_key = storage_service.make_selfie_key(event_id, session_id)
        import io
        selfie_url = storage_service.upload_file(
            io.BytesIO(content), selfie_key, content_type="image/jpeg"
        )

        # Create/update session record
        new_token = session_token or secrets.token_urlsafe(32)
        session = await self.session_repo.create(
            event_id=event_id,
            session_token=new_token,
            query_image_url=selfie_url,
            index_version=event.index_version,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )

        # Queue AI search task (synchronous result via Celery chord or polling)
        # For MVP: trigger task and return session token for polling
        celery_app.send_task(
            "worker.tasks.process_image.search_faces_task",
            kwargs={
                "session_id": str(session.id),
                "event_id": str(event_id),
                "selfie_url": selfie_url,
            },
            queue="ai_processing",
        )

        return {
            "session_token": new_token,
            "from_cache": False,
            "status": "processing",
            "message": "Search initiated. Poll /search/results/{session_token} for results.",
        }

    async def get_search_results(self, session_token: str) -> dict:
        """Poll for search results by session token."""
        session = await self.session_repo.get_by_token(session_token)
        if not session:
            raise NotFoundError("SearchSession", session_token)

        if session.matched_image_ids is None:
            return {"status": "processing", "images": []}

        # Map image IDs back to metadata
        image_ids = [uuid.UUID(i) for i in session.matched_image_ids]
        images = []
        for image_id in image_ids:
            img = await self.image_repo.get_by_id(image_id)
            if img:
                images.append(img)

        return {
            "status": "completed",
            "session_token": session_token,
            "images": images,
        }
