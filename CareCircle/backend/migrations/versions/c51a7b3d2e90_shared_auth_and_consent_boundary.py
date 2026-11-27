"""Use platform authentication and separate reported consent from personal consent.

Revision ID: c51a7b3d2e90
Revises: f19e51001d9a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c51a7b3d2e90"
down_revision: Union[str, Sequence[str], None] = "f19e51001d9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "parent_consents",
        sa.Column("consent_source", sa.String(length=32), nullable=True),
    )
    with op.batch_alter_table("parent_consents") as batch_op:
        batch_op.alter_column(
            "effective_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=True,
        )
    op.execute(
        "UPDATE parent_consents "
        "SET consent_source = 'family_reported', "
        "status = CASE WHEN status = 'active' THEN 'family_reported' ELSE status END, "
        "effective_at = NULL"
    )
    with op.batch_alter_table("parent_consents") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=32),
            server_default="family_reported",
        )
        batch_op.alter_column(
            "consent_source",
            existing_type=sa.String(length=32),
            nullable=False,
            server_default="family_reported",
        )
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("password_hash")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("password_hash", sa.String(length=255), nullable=True))
    with op.batch_alter_table("parent_consents") as batch_op:
        batch_op.drop_column("consent_source")
    op.execute(
        "UPDATE parent_consents SET status = 'active' "
        "WHERE status = 'family_reported'"
    )
