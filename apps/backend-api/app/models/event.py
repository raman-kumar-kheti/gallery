import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, BigInteger, Integer, DateTime, func, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class EventStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"
    expired = "expired"


class EventType(str, enum.Enum):
    wedding = "wedding"
    corporate = "corporate"
    birthday = "birthday"
    conference = "conference"
    sports = "sports"
    other = "other"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[EventType] = mapped_column(
        SAEnum(EventType), nullable=False, default=EventType.other
    )
    status: Mapped[EventStatus] = mapped_column(
        SAEnum(EventStatus), nullable=False, default=EventStatus.draft
    )
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    image_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # FAISS index path relative to FAISS_INDEX_DIR e.g. "event_{id}.index"
    faiss_index_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Incremented every time the FAISS index is rebuilt — used for cache invalidation
    index_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    owner: Mapped[Optional["User"]] = relationship(
        back_populates="owned_events", foreign_keys=[owner_user_id]
    )
    organization: Mapped[Optional["Organization"]] = relationship(
        back_populates="events", foreign_keys=[organization_id]
    )
    images: Mapped[list["Image"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    qr_codes: Mapped[list["QRCode"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    search_sessions: Mapped[list["SearchSession"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    uploaders: Mapped[list["EventUploader"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="event")

    def __repr__(self) -> str:
        return f"<Event id={self.id} slug={self.slug}>"


class EventUploader(Base):
    """Temporary upload access — for customer-invited photographers."""

    __tablename__ = "event_uploaders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    permissions: Mapped[str] = mapped_column(
        String(255), nullable=False, default="upload_images"
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="uploaders")
    user: Mapped["User"] = relationship()
