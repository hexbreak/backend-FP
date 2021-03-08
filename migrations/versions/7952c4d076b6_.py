"""empty message

Revision ID: 7952c4d076b6
Revises: 6290576b1e2a
Create Date: 2021-03-08 14:56:50.042707

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7952c4d076b6'
down_revision = '6290576b1e2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('now_playing', 'game_id',
               existing_type=mysql.VARCHAR(length=120),
               nullable=False)
    op.alter_column('now_playing', 'game_name',
               existing_type=mysql.VARCHAR(length=250),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('now_playing', 'game_name',
               existing_type=mysql.VARCHAR(length=250),
               nullable=True)
    op.alter_column('now_playing', 'game_id',
               existing_type=mysql.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###
