from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.models.search_session import SearchSession


class SearchSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_token(self, session_token: str) -> Optional[SearchSession]:
        result = await self.db.execute(
            select(SearchSession).where(
                and_(
                    SearchSession.session_token == session_token,
                    SearchSession.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> SearchSession:
        session = SearchSession(**kwargs)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def update(self, session: SearchSession, **kwargs) -> SearchSession:
        for key, value in kwargs.items():
            setattr(session, key, value)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def is_cache_valid(
        self, session: SearchSession, current_index_version: int
    ) -> bool:
        """Check if cached results are still valid (index not rebuilt since search)."""
        return (
            session.matched_image_ids is not None
            and session.index_version == current_index_version
        )
