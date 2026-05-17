"""
Audit logging helper — call from services to record actions.
"""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


async def log_action(
    db: AsyncSession,
    action: str,
    user_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Insert an audit log entry.

    Usage:
        await log_action(db, "event.created", user_id=user.id,
                         resource_type="event", resource_id=str(event.id))
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        meta_data=metadata,
        ip_address=ip_address,
    )
    db.add(entry)
    # Don't flush here — caller commits the transaction
