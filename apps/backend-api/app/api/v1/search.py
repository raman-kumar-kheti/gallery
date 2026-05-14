from fastapi import APIRouter, Depends, UploadFile, File, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.database import get_db
from app.services.search_service import SearchService
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.post("/selfie/{event_id}")
async def search_by_selfie(
    event_id: uuid.UUID,
    selfie: UploadFile = File(...),
    x_session_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Guest selfie search endpoint.
    No auth required — guests access via QR code token which resolves to event_id.
    Optional X-Session-Token header for result caching.
    """
    service = SearchService(db)
    result = await service.search_by_selfie(
        event_id=event_id,
        selfie_file=selfie,
        session_token=x_session_token,
    )
    return result


@router.get("/results/{session_token}")
async def get_search_results(
    session_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Poll for search results. Guest stores session_token in localStorage after selfie upload.
    Returns 'processing' status until AI worker completes.
    """
    service = SearchService(db)
    result = await service.get_search_results(session_token)

    if result["status"] == "completed":
        images = result["images"]
        return {
            "status": "completed",
            "session_token": session_token,
            "match_count": len(images),
            "images": [
                {
                    "id": str(img.id),
                    "image_url": img.image_url,
                    "thumbnail_url": img.thumbnail_url,
                    "width": img.width,
                    "height": img.height,
                }
                for img in images
            ],
        }
    return result
