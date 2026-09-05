"""Initial Nexora domain tables.

Revision ID: 20260905_0001
Revises:
Create Date: 2026-09-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260905_0001"
down_revision = None
branch_labels = None
depends_on = None

membership_role = sa.Enum("OWNER", "ADMIN", "MEMBER", name="membership_role")
dataset_status = sa.Enum("PENDING_UPLOAD", "QUEUED", "PROCESSING", "READY", "FAILED", name="dataset_status")


def upgrade() -> None:
    bind = op.get_bind()
    membership_role.create(bind, checkfirst=True)
    dataset_status.create(bind, checkfirst=True)
    op.create_table("users", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("email", sa.String(320), nullable=False, unique=True), sa.Column("name", sa.String(200)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("organizations", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("slug", sa.String(220), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_organizations_slug", "organizations", ["slug"])
    op.create_table("memberships", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("role", membership_role, nullable=False, server_default="MEMBER"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.UniqueConstraint("user_id", "organization_id"))
    op.create_index("ix_memberships_org", "memberships", ["organization_id"])
    op.create_table("datasets", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("source_path", sa.String(1024), nullable=False, unique=True), sa.Column("content_type", sa.String(100), nullable=False), sa.Column("status", dataset_status, nullable=False, server_default="PENDING_UPLOAD"), sa.Column("profile", postgresql.JSONB()), sa.Column("error_message", sa.String(1000)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_datasets_org", "datasets", ["organization_id"])
    op.create_table("audit_logs", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("action", sa.String(100), nullable=False), sa.Column("target_type", sa.String(100), nullable=False), sa.Column("target_id", sa.String(100)), sa.Column("metadata", postgresql.JSONB()), sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_audit_logs_org_created", "audit_logs", ["organization_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("datasets")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")
    dataset_status.drop(op.get_bind(), checkfirst=True)
    membership_role.drop(op.get_bind(), checkfirst=True)
