"""add magazines table

Revision ID: a1b2c3d4e5f6
Revises: 94a5041843e2
Create Date: 2026-08-01 15:37:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '94a5041843e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('magazines',
        sa.Column('magazine_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('pdf_url', sa.String(length=1024), nullable=False),
        sa.Column('cover_image_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('magazine_id')
    )


def downgrade() -> None:
    op.drop_table('magazines')
