"""Add soft delete columns to financial_records

Revision ID: 20260402_0002
Revises: 20260401_0001
Create Date: 2026-04-02
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260402_0002"
down_revision = "20260401_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "financial_records",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("financial_records", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_financial_records_is_deleted", "financial_records", ["is_deleted"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_financial_records_is_deleted", table_name="financial_records")
    op.drop_column("financial_records", "deleted_at")
    op.drop_column("financial_records", "is_deleted")
