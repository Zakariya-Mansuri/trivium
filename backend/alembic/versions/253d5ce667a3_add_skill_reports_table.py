# add skill_reports table
#
# Revision ID: 253d5ce667a3
# Revises: 528e4ffa07ac
# Create Date: 2026-07-26 19:47:52.166974

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import app.db.base

revision: str = '253d5ce667a3'
down_revision: Union[str, None] = '528e4ffa07ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dev databases may already have this table via the app's create_all bootstrap.
    from sqlalchemy import inspect

    if inspect(op.get_bind()).has_table('skill_reports'):
        return
    op.create_table(
        'skill_reports',
        sa.Column('id', app.db.base.GUID(length=36), nullable=False),
        sa.Column('user_id', app.db.base.GUID(length=36), nullable=False),
        sa.Column('report_type', sa.String(length=20), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.Column('computed_at', app.db.base.UTCDateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_skill_reports_user_type', 'skill_reports', ['user_id', 'report_type'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_skill_reports_user_type', table_name='skill_reports')
    op.drop_table('skill_reports')
