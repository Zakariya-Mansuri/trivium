# add ai_performance to review_history
#
# Revision ID: 7b1c9aa41f02
# Revises: 253d5ce667a3
# Create Date: 2026-07-26 21:05:00.000000

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '7b1c9aa41f02'
down_revision: Union[str, None] = '253d5ce667a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('review_history', sa.Column('ai_performance', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('review_history', 'ai_performance')
