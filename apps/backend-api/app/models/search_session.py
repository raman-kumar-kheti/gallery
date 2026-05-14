import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class SearchSession(Base):
    """
    Caches guest search results to avoid repeated selfie uploads and FAISS queries.
    Session is keyed by a temporary token stored in the guest's browser (localStorage/cookie).
    """

    __tablename__ = "search_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Token sent to guest's browser — used to retrieve cached results
    session_token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    # URL of the uploaded selfie in R2
    query_image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    # Array of matched image UUIDs: ["uuid1", "uuid2", ...]
    matched_image_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    # Snapshot of event's index_version at search time — used to detect stale cache
    index_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="search_sessions")

    def __repr__(self) -> str:
        return f"<SearchSession id={self.id} token={self.session_token}>"
