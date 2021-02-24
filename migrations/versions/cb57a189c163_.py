"""empty message

Revision ID: cb57a189c163
Revises: dc272a792f2b
Create Date: 2021-02-23 20:47:06.519328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb57a189c163'
down_revision = 'dc272a792f2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('backlog', sa.Column('game_genre', sa.String(length=250), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('backlog', 'game_genre')
    # ### end Alembic commands ###
