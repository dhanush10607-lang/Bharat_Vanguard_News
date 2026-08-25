"""add translations to ai_summaries

Revision ID: a2b3c4d5e6f7
Revises: 0fe51ee41b0b
Create Date: 2026-08-25 22:59:38.535960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = '0fe51ee41b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ai_summaries', sa.Column('translations', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

def downgrade() -> None:
    op.drop_column('ai_summaries', 'translations')
