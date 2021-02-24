"""empty message

Revision ID: d13369440c13
Revises: cb57a189c163
Create Date: 2021-02-23 22:48:32.222768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd13369440c13'
down_revision = 'cb57a189c163'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('game_genre', table_name='genre')
    op.drop_index('game_id', table_name='genre')
    op.drop_table('genre')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_backlog_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('game_id', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('game_genre', mysql.VARCHAR(length=250), nullable=False),
    sa.ForeignKeyConstraint(['user_backlog_id'], ['backlog.id'], name='genre_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('game_id', 'genre', ['game_id'], unique=True)
    op.create_index('game_genre', 'genre', ['game_genre'], unique=True)
    # ### end Alembic commands ###