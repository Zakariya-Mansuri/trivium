# add user llm provider columns (BYOK)
#
# Revision ID: 9c4e21d0aa15
# Revises: 7b1c9aa41f02
# Create Date: 2026-07-26 22:20:00.000000

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9c4e21d0aa15'
down_revision: Union[str, None] = '7b1c9aa41f02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy import inspect

    columns = {c['name'] for c in inspect(op.get_bind()).get_columns('users')}
    if 'llm_provider' not in columns:
        op.add_column('users', sa.Column('llm_provider', sa.String(length=30), nullable=True))
    if 'llm_model' not in columns:
        op.add_column('users', sa.Column('llm_model', sa.String(length=120), nullable=True))
    if 'llm_api_key_enc' not in columns:
        op.add_column('users', sa.Column('llm_api_key_enc', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'llm_api_key_enc')
    op.drop_column('users', 'llm_model')
    op.drop_column('users', 'llm_provider')
