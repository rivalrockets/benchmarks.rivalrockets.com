"""add revokedtoken

Revision ID: bbdff842b0cb
Revises: ad580d7b4f2a
Create Date: 2018-08-22 23:34:44.240714

"""

# revision identifiers, used by Alembic.
revision = 'bbdff842b0cb'
down_revision = 'ad580d7b4f2a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('revoked_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jti', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('revoked_tokens')
    # ### end Alembic commands ###
