import uuid
import urllib.request
import io
import logging
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from worker.celery_app import celery_app
from worker.config import settings
from worker.services.face_service import face_service
from worker.services.faiss_service import faiss_service
from worker.services.thumbnail_service import thumbnail_service

logger = logging.getLogger(__name__)

# Sync SQLAlchemy engine for Celery worker
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    return SessionLocal()


def _download_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        return response.read()


def _upload_to_r2(data: bytes, key: str, content_type: str = "image/jpeg") -> str:
    """Upload bytes to R2 and return public URL."""
    import boto3
    from botocore.config import Config

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    client.upload_fileobj(
        io.BytesIO(data),
        settings.r2_bucket_name,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return f"{settings.r2_public_url}/{key}"


@celery_app.task(
    name="worker.tasks.process_image.process_image_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def process_image_task(self, image_id: str, event_id: str, image_url: str):
    """
    Full AI processing pipeline for a single uploaded image:
    1. Download image from R2
    2. Generate thumbnail → upload to R2
    3. Extract face embedding(s) via InsightFace
    4. Add embedding to event's FAISS index
    5. Save faiss_pos to PostgreSQL
    6. Update image status to 'completed'
    """
    db = get_db()
    try:
        from sqlalchemy import text

        # Mark as processing
        db.execute(
            text("UPDATE images SET processing_status = 'processing' WHERE id = :id"),
            {"id": image_id},
        )
        db.commit()

        # 1. Download image
        logger.info(f"Downloading image {image_id} from {image_url}")
        image_bytes = _download_bytes(image_url)

        # 2. Generate thumbnail
        thumb_bytes = thumbnail_service.generate_thumbnail(image_bytes)
        width, height = thumbnail_service.get_dimensions(image_bytes)

        thumb_key = f"events/{event_id}/thumbnails/{image_id}_thumb.jpg"
        thumb_url = _upload_to_r2(thumb_bytes, thumb_key, "image/jpeg")

        # 3. Extract face embeddings
        img_array = face_service.load_image_from_bytes(image_bytes)
        embeddings = face_service.get_all_embeddings(img_array)

        faiss_pos = None
        if embeddings:
            # Use first/primary face embedding
            primary_embedding = embeddings[0]
            faiss_pos = faiss_service.add_embedding(event_id, primary_embedding)
            logger.info(f"Image {image_id}: face indexed at FAISS pos {faiss_pos}")
        else:
            logger.warning(f"Image {image_id}: no face detected, skipping FAISS indexing")

        # 4. Update PostgreSQL
        db.execute(
            text("""
                UPDATE images SET
                    thumbnail_url = :thumb_url,
                    width = :width,
                    height = :height,
                    faiss_pos = :faiss_pos,
                    processing_status = 'completed'
                WHERE id = :id
            """),
            {
                "thumb_url": thumb_url,
                "width": width,
                "height": height,
                "faiss_pos": faiss_pos,
                "id": image_id,
            },
        )
        db.commit()
        logger.info(f"Image {image_id} processing completed")

    except Exception as exc:
        db.rollback()
        logger.error(f"Image {image_id} processing failed: {exc}")

        # Mark as failed
        try:
            from sqlalchemy import text as t2
            db.execute(
                t2("UPDATE images SET processing_status = 'failed', processing_error = :err WHERE id = :id"),
                {"err": str(exc)[:500], "id": image_id},
            )
            db.commit()
        except Exception:
            db.rollback()

        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(
    name="worker.tasks.process_image.search_faces_task",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def search_faces_task(self, session_id: str, event_id: str, selfie_url: str):
    """
    Guest search pipeline:
    1. Download selfie from R2
    2. Extract face embedding
    3. Search event FAISS index
    4. Map faiss_pos → image IDs in PostgreSQL
    5. Save matched_image_ids to search_sessions
    """
    db = get_db()
    try:
        from sqlalchemy import text

        # 1. Download selfie
        selfie_bytes = _download_bytes(selfie_url)

        # 2. Extract embedding
        img_array = face_service.load_image_from_bytes(selfie_bytes)
        embedding = face_service.get_embedding(img_array)

        if embedding is None:
            # No face found in selfie
            db.execute(
                text("UPDATE search_sessions SET matched_image_ids = '[]'::jsonb WHERE id = :id"),
                {"id": session_id},
            )
            db.commit()
            return

        # 3. FAISS search
        matched_positions = faiss_service.search(event_id, embedding, top_k=50)

        # 4. Map faiss_pos → image IDs
        if matched_positions:
            placeholders = ",".join(str(p) for p in matched_positions)
            result = db.execute(
                text(f"""
                    SELECT id FROM images
                    WHERE event_id = :event_id
                      AND faiss_pos IN ({placeholders})
                      AND processing_status = 'completed'
                """),
                {"event_id": event_id},
            )
            image_ids = [str(row[0]) for row in result.fetchall()]
        else:
            image_ids = []

        # 5. Update search session
        import json
        db.execute(
            text("""
                UPDATE search_sessions
                SET matched_image_ids = :ids::jsonb
                WHERE id = :id
            """),
            {"ids": json.dumps(image_ids), "id": session_id},
        )
        db.commit()
        logger.info(f"Search session {session_id}: found {len(image_ids)} matches")

    except Exception as exc:
        db.rollback()
        logger.error(f"Search task failed for session {session_id}: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()
