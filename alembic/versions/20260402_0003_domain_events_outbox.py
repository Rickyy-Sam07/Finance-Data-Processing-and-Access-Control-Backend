"""Add domain events outbox table

Revision ID: 20260402_0003
Revises: 20260402_0002
Create Date: 2026-04-02
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260402_0003"
down_revision = "20260402_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domain_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_id", sa.String(length=120), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("error", sa.String(length=500), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_domain_events_id", "domain_events", ["id"], unique=False)
    op.create_index("ix_domain_events_status", "domain_events", ["status"], unique=False)
    op.create_index("ix_domain_events_event_type", "domain_events", ["event_type"], unique=False)
    op.create_index("ix_domain_events_aggregate_type", "domain_events", ["aggregate_type"], unique=False)
    op.create_index("ix_domain_events_aggregate_id", "domain_events", ["aggregate_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_domain_events_aggregate_id", table_name="domain_events")
    op.drop_index("ix_domain_events_aggregate_type", table_name="domain_events")
    op.drop_index("ix_domain_events_event_type", table_name="domain_events")
    op.drop_index("ix_domain_events_status", table_name="domain_events")
    op.drop_index("ix_domain_events_id", table_name="domain_events")
    op.drop_table("domain_events")
