import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Enum as SAEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class AccountType(str, enum.Enum):
    studio = "studio"
    photographer = "photographer"
    customer = "customer"


class AuthProvider(str, enum.Enum):
    google = "google"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(
        SAEnum(AuthProvider), nullable=False, default=AuthProvider.google
    )
    auth_provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_type: Mapped[Optional[AccountType]] = mapped_column(
        SAEnum(AccountType), nullable=True  # null until onboarding complete
    )
    onboarding_completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    owned_organizations: Mapped[list["Organization"]] = relationship(
        back_populates="owner", foreign_keys="Organization.owner_user_id"
    )
    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user"
    )
    owned_events: Mapped[list["Event"]] = relationship(
        back_populates="owner", foreign_keys="Event.owner_user_id"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
