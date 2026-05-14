import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from worker.celery_app import celery_app
from worker.config import settings
from worker.services.face_service import face_service
from worker.services.faiss_service import faiss_service

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(
    name="worker.tasks.rebuild_index.rebuild_event_index",
    bind=True,
    max_retries=2,
)
def rebuild_event_index(self, event_id: str):
    """
    Rebuild the entire FAISS index for an event from scratch.
    Used after bulk deletions or index corruption.

    Process:
    1. Load all completed images with their faiss_pos and image_urls
    2. Re-download and re-embed each image
    3. Rebuild FAISS index with fresh embeddings
    4. Reassign faiss_pos values in PostgreSQL
    5. Increment event.index_version to invalidate search caches
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting index rebuild for event {event_id}")

        # Get all completed images for this event
        result = db.execute(
            text("""
                SELECT id, image_url, faiss_pos
                FROM images
                WHERE event_id = :event_id
                  AND processing_status = 'completed'
                ORDER BY created_at ASC
            """),
            {"event_id": event_id},
        )
        images = result.fetchall()

        embeddings = []
        image_ids_ordered = []

        for idx, (image_id, image_url, _old_pos) in enumerate(images):
            try:
                import urllib.request
                with urllib.request.urlopen(image_url) as resp:
                    image_bytes = resp.read()

                img_array = face_service.load_image_from_bytes(image_bytes)
                embedding = face_service.get_embedding(img_array)

                if embedding is not None:
                    embeddings.append(embedding)
                    image_ids_ordered.append((image_id, len(embeddings) - 1))
                    logger.debug(f"Embedded image {image_id} at new pos {len(embeddings) - 1}")
            except Exception as e:
                logger.warning(f"Failed to re-embed image {image_id}: {e}")

        # Rebuild FAISS index
        if embeddings:
            faiss_service.rebuild_index(event_id, embeddings)

        # Update faiss_pos in PostgreSQL
        for image_id, new_pos in image_ids_ordered:
            db.execute(
                text("UPDATE images SET faiss_pos = :pos WHERE id = :id"),
                {"pos": new_pos, "id": str(image_id)},
            )

        # Clear faiss_pos for images that no longer have embeddings
        all_updated_ids = [str(img_id) for img_id, _ in image_ids_ordered]
        if all_updated_ids:
            db.execute(
                text("""
                    UPDATE images SET faiss_pos = NULL
                    WHERE event_id = :event_id
                      AND id NOT IN :ids
                """).bindparams(
                    event_id=event_id, ids=tuple(all_updated_ids) if all_updated_ids else ("",)
                )
            )

        # Increment index_version to invalidate cached search sessions
        db.execute(
            text("UPDATE events SET index_version = index_version + 1 WHERE id = :id"),
            {"id": event_id},
        )
        db.commit()

        logger.info(
            f"Index rebuild complete for event {event_id}: "
            f"{len(embeddings)} vectors indexed, version incremented"
        )

    except Exception as exc:
        db.rollback()
        logger.error(f"Index rebuild failed for event {event_id}: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()
