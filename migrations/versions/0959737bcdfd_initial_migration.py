"""initial migration

Revision ID: 0959737bcdfd
Revises: None
Create Date: 2016-10-17 22:36:44.528154

"""

# revision identifiers, used by Alembic.
revision = '0959737bcdfd'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('machines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system_name', sa.Text(), nullable=True),
    sa.Column('system_notes', sa.Text(), nullable=True),
    sa.Column('system_notes_html', sa.Text(), nullable=True),
    sa.Column('owner', sa.Text(), nullable=True),
    sa.Column('active_revision_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['active_revision_id'], ['machines.id'], ),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_machines_timestamp'), 'machines', ['timestamp'], unique=False)
    op.create_table('revisions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cpu_make', sa.String(length=64), nullable=True),
    sa.Column('cpu_name', sa.String(length=64), nullable=True),
    sa.Column('cpu_socket', sa.String(length=64), nullable=True),
    sa.Column('cpu_mhz', sa.Integer(), nullable=True),
    sa.Column('cpu_proc_cores', sa.Integer(), nullable=True),
    sa.Column('chipset', sa.String(length=64), nullable=True),
    sa.Column('system_memory_gb', sa.Integer(), nullable=True),
    sa.Column('system_memory_mhz', sa.Integer(), nullable=True),
    sa.Column('gpu_name', sa.String(length=64), nullable=True),
    sa.Column('gpu_make', sa.String(length=64), nullable=True),
    sa.Column('gpu_memory_mb', sa.Integer(), nullable=True),
    sa.Column('gpu_count', sa.Integer(), nullable=True),
    sa.Column('revision_notes', sa.Text(), nullable=True),
    sa.Column('revision_notes_html', sa.Text(), nullable=True),
    sa.Column('pcpartpicker_url', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('machine_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_revisions_timestamp'), 'revisions', ['timestamp'], unique=False)
    op.create_table('cinebenchr15results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result_date', sa.DateTime(), nullable=True),
    sa.Column('cpu_cb', sa.Integer(), nullable=True),
    sa.Column('opengl_fps', sa.Integer(), nullable=True),
    sa.Column('revision_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['revision_id'], ['revisions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cinebenchr15results_cpu_cb'), 'cinebenchr15results', ['cpu_cb'], unique=False)
    op.create_index(op.f('ix_cinebenchr15results_opengl_fps'), 'cinebenchr15results', ['opengl_fps'], unique=False)
    op.create_index(op.f('ix_cinebenchr15results_result_date'), 'cinebenchr15results', ['result_date'], unique=False)
    op.create_table('futuremark3dmarkresults',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result_date', sa.DateTime(), nullable=True),
    sa.Column('icestorm_score', sa.Integer(), nullable=True),
    sa.Column('icestorm_result_url', sa.String(), nullable=True),
    sa.Column('cloudgate_score', sa.Integer(), nullable=True),
    sa.Column('cloudgate_result_url', sa.String(), nullable=True),
    sa.Column('firestrike_score', sa.Integer(), nullable=True),
    sa.Column('firestrike_result_url', sa.String(), nullable=True),
    sa.Column('skydiver_score', sa.Integer(), nullable=True),
    sa.Column('skydiver_result_url', sa.String(), nullable=True),
    sa.Column('overall_result_url', sa.String(), nullable=True),
    sa.Column('revision_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['revision_id'], ['revisions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_futuremark3dmarkresults_cloudgate_score'), 'futuremark3dmarkresults', ['cloudgate_score'], unique=False)
    op.create_index(op.f('ix_futuremark3dmarkresults_firestrike_score'), 'futuremark3dmarkresults', ['firestrike_score'], unique=False)
    op.create_index(op.f('ix_futuremark3dmarkresults_icestorm_score'), 'futuremark3dmarkresults', ['icestorm_score'], unique=False)
    op.create_index(op.f('ix_futuremark3dmarkresults_result_date'), 'futuremark3dmarkresults', ['result_date'], unique=False)
    op.create_index(op.f('ix_futuremark3dmarkresults_skydiver_score'), 'futuremark3dmarkresults', ['skydiver_score'], unique=False)
    ### end Alembic commands ###


def downgrade():
    op.drop_index(op.f('ix_futuremark3dmarkresults_skydiver_score'), table_name='futuremark3dmarkresults')
    op.drop_index(op.f('ix_futuremark3dmarkresults_result_date'), table_name='futuremark3dmarkresults')
    op.drop_index(op.f('ix_futuremark3dmarkresults_icestorm_score'), table_name='futuremark3dmarkresults')
    op.drop_index(op.f('ix_futuremark3dmarkresults_firestrike_score'), table_name='futuremark3dmarkresults')
    op.drop_index(op.f('ix_futuremark3dmarkresults_cloudgate_score'), table_name='futuremark3dmarkresults')
    op.drop_table('futuremark3dmarkresults')
    op.drop_index(op.f('ix_cinebenchr15results_result_date'), table_name='cinebenchr15results')
    op.drop_index(op.f('ix_cinebenchr15results_opengl_fps'), table_name='cinebenchr15results')
    op.drop_index(op.f('ix_cinebenchr15results_cpu_cb'), table_name='cinebenchr15results')
    op.drop_table('cinebenchr15results')
    op.drop_index(op.f('ix_revisions_timestamp'), table_name='revisions')
    op.drop_table('revisions')
    op.drop_index(op.f('ix_machines_timestamp'), table_name='machines')
    op.drop_table('machines')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    ### end Alembic commands ###
