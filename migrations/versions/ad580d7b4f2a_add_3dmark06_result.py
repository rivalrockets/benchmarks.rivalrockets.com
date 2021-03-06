"""Add 3DMark06 Result

Revision ID: ad580d7b4f2a
Revises: 0959737bcdfd
Create Date: 2016-10-23 13:47:14.849821

"""

# revision identifiers, used by Alembic.
revision = 'ad580d7b4f2a'
down_revision = '0959737bcdfd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic ###
    op.create_table('futuremark3dmark06results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result_date', sa.DateTime(), nullable=True),
    sa.Column('sm2_score', sa.Integer(), nullable=True),
    sa.Column('cpu_score', sa.Integer(), nullable=True),
    sa.Column('sm3_score', sa.Integer(), nullable=True),
    sa.Column('proxcyon_fps', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('fireflyforest_fps', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('cpu1_fps', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('cpu2_fps', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('canyonflight_fps', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('deepfreeze_fps', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('overall_score', sa.Integer(), nullable=True),
    sa.Column('result_url', sa.String(), nullable=True),
    sa.Column('revision_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['revision_id'], ['revisions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_futuremark3dmark06results_cpu_score'), 'futuremark3dmark06results', ['cpu_score'], unique=False)
    op.create_index(op.f('ix_futuremark3dmark06results_overall_score'), 'futuremark3dmark06results', ['overall_score'], unique=False)
    op.create_index(op.f('ix_futuremark3dmark06results_result_date'), 'futuremark3dmark06results', ['result_date'], unique=False)
    op.create_index(op.f('ix_futuremark3dmark06results_sm2_score'), 'futuremark3dmark06results', ['sm2_score'], unique=False)
    op.create_index(op.f('ix_futuremark3dmark06results_sm3_score'), 'futuremark3dmark06results', ['sm3_score'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic ###
    op.drop_index(op.f('ix_futuremark3dmark06results_sm3_score'), table_name='futuremark3dmark06results')
    op.drop_index(op.f('ix_futuremark3dmark06results_sm2_score'), table_name='futuremark3dmark06results')
    op.drop_index(op.f('ix_futuremark3dmark06results_result_date'), table_name='futuremark3dmark06results')
    op.drop_index(op.f('ix_futuremark3dmark06results_overall_score'), table_name='futuremark3dmark06results')
    op.drop_index(op.f('ix_futuremark3dmark06results_cpu_score'), table_name='futuremark3dmark06results')
    op.drop_table('futuremark3dmark06results')
    ### end Alembic commands ###
