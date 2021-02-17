"""empty message

Revision ID: 7eb05ba94482
Revises: 9e4248f15bde
Create Date: 2021-02-17 06:27:24.479242

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7eb05ba94482'
down_revision = '9e4248f15bde'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_backlog_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.String(length=250), nullable=False),
    sa.Column('game_genre', sa.String(length=250), nullable=False),
    sa.ForeignKeyConstraint(['user_backlog_id'], ['backlog.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('game_genre'),
    sa.UniqueConstraint('game_id')
    )
    op.add_column('now_playing', sa.Column('user_backlog_id', sa.Integer(), nullable=False))
    op.drop_constraint('now_playing_ibfk_1', 'now_playing', type_='foreignkey')
    op.create_foreign_key(None, 'now_playing', 'backlog', ['user_backlog_id'], ['id'])
    op.drop_column('now_playing', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('now_playing', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'now_playing', type_='foreignkey')
    op.create_foreign_key('now_playing_ibfk_1', 'now_playing', 'user', ['user_id'], ['id'])
    op.drop_column('now_playing', 'user_backlog_id')
    op.drop_table('genre')
    # ### end Alembic commands ###
