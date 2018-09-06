"""add permissions and roles

Revision ID: 556574b57514
Revises: bbdff842b0cb
Create Date: 2018-09-06 00:00:17.419441

"""

# revision identifiers, used by Alembic.
revision = '556574b57514'
down_revision = 'bbdff842b0cb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles')),
    sa.UniqueConstraint('name', name=op.f('uq_roles_name'))
    )
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roles_default'), ['default'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_users_role_id_roles'), 'roles', ['role_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_users_role_id_roles'), type_='foreignkey')
        batch_op.drop_column('role_id')

    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roles_default'))

    op.drop_table('roles')
    # ### end Alembic commands ###
