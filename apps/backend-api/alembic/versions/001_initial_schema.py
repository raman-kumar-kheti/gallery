"""Initial schema — all tables

Revision ID: 001
Revises:
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column(
            "auth_provider",
            sa.Enum("google", name="authprovider"),
            nullable=False,
        ),
        sa.Column("auth_provider_id", sa.String(255), nullable=True),
        sa.Column(
            "account_type",
            sa.Enum("studio", "photographer", "customer", name="accounttype"),
            nullable=True,
        ),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── roles ─────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
    )

    # ── permissions ───────────────────────────────────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
    )

    # ── role_permissions ──────────────────────────────────────────────────
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )

    # ── organizations ─────────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("storage_limit_bytes", sa.BigInteger(), nullable=False, server_default="10737418240"),
        sa.Column("storage_used_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── organization_members ──────────────────────────────────────────────
    op.create_table(
        "organization_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_org_members_org_id", "organization_members", ["organization_id"])

    # ── plans ─────────────────────────────────────────────────────────────
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("storage_limit_bytes", sa.BigInteger(), nullable=False),
        sa.Column("event_limit", sa.Integer(), nullable=True),
        sa.Column("monthly_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # ── subscriptions ─────────────────────────────────────────────────────
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.Enum("active", "past_due", "cancelled", "trialing", name="subscriptionstatus"), nullable=False),
        sa.Column("razorpay_subscription_id", sa.String(255), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_subscriptions_org_id", "subscriptions", ["organization_id"])

    # ── events ────────────────────────────────────────────────────────────
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", sa.Enum("wedding", "corporate", "birthday", "conference", "sports", "other", name="eventtype"), nullable=False, server_default="other"),
        sa.Column("status", sa.Enum("draft", "active", "archived", "expired", name="eventstatus"), nullable=False, server_default="draft"),
        sa.Column("storage_used_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("image_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("faiss_index_path", sa.String(500), nullable=True),
        sa.Column("index_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_events_org_id", "events", ["organization_id"])
    op.create_index("ix_events_owner_id", "events", ["owner_user_id"])

    # ── event_uploaders ───────────────────────────────────────────────────
    op.create_table(
        "event_uploaders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permissions", sa.String(255), nullable=False, server_default="upload_images"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_event_uploaders_event_id", "event_uploaders", ["event_id"])

    # ── images ────────────────────────────────────────────────────────────
    op.create_table(
        "images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("image_url", sa.String(1000), nullable=False),
        sa.Column("thumbnail_url", sa.String(1000), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("mime_type", sa.String(100), nullable=False, server_default="image/jpeg"),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("faiss_pos", sa.Integer(), nullable=True),
        sa.Column("processing_status", sa.Enum("pending", "processing", "completed", "failed", name="processingstatus"), nullable=False, server_default="pending"),
        sa.Column("processing_error", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_images_event_id", "images", ["event_id"])
    op.create_index("ix_images_faiss_pos", "images", ["faiss_pos"])

    # ── payments ──────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="INR"),
        sa.Column("provider", sa.Enum("razorpay", name="paymentprovider"), nullable=False),
        sa.Column("provider_payment_id", sa.String(255), nullable=True),
        sa.Column("provider_order_id", sa.String(255), nullable=True),
        sa.Column("status", sa.Enum("pending", "captured", "failed", "refunded", name="paymentstatus"), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_payments_provider_payment_id", "payments", ["provider_payment_id"])

    # ── qr_codes ──────────────────────────────────────────────────────────
    op.create_table(
        "qr_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("qr_token", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_qr_codes_token", "qr_codes", ["qr_token"], unique=True)

    # ── search_sessions ───────────────────────────────────────────────────
    op.create_table(
        "search_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_token", sa.String(255), nullable=False, unique=True),
        sa.Column("query_image_url", sa.String(1000), nullable=True),
        sa.Column("matched_image_ids", postgresql.JSONB(), nullable=True),
        sa.Column("index_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_search_sessions_token", "search_sessions", ["session_token"], unique=True)

    # ── audit_logs ────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Seed roles and permissions ─────────────────────────────────────────
    import uuid as _uuid
    from datetime import datetime

    role_ids = {
        "owner": str(_uuid.uuid4()),
        "manager": str(_uuid.uuid4()),
        "uploader": str(_uuid.uuid4()),
    }
    permission_ids = {
        "create_event": str(_uuid.uuid4()),
        "upload_images": str(_uuid.uuid4()),
        "manage_users": str(_uuid.uuid4()),
        "manage_billing": str(_uuid.uuid4()),
        "view_analytics": str(_uuid.uuid4()),
        "delete_event": str(_uuid.uuid4()),
    }
    role_permissions_map = {
        "owner": ["create_event", "upload_images", "manage_users", "manage_billing", "view_analytics", "delete_event"],
        "manager": ["create_event", "upload_images", "view_analytics", "delete_event"],
        "uploader": ["upload_images"],
    }

    op.bulk_insert(
        sa.table("roles", sa.column("id"), sa.column("name")),
        [{"id": role_ids[r], "name": r} for r in role_ids],
    )
    op.bulk_insert(
        sa.table("permissions", sa.column("id"), sa.column("key")),
        [{"id": permission_ids[p], "key": p} for p in permission_ids],
    )
    role_perm_rows = []
    for role, perms in role_permissions_map.items():
        for perm in perms:
            role_perm_rows.append({
                "role_id": role_ids[role],
                "permission_id": permission_ids[perm],
            })
    op.bulk_insert(
        sa.table("role_permissions", sa.column("role_id"), sa.column("permission_id")),
        role_perm_rows,
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("search_sessions")
    op.drop_table("qr_codes")
    op.drop_table("payments")
    op.drop_table("images")
    op.drop_table("event_uploaders")
    op.drop_table("events")
    op.drop_table("subscriptions")
    op.drop_table("plans")
    op.drop_table("organization_members")
    op.drop_table("organizations")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")

    # Drop enums
    for enum_name in [
        "authprovider", "accounttype", "eventstatus", "eventtype",
        "processingstatus", "subscriptionstatus", "paymentprovider", "paymentstatus"
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
