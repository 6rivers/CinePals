"""empty message

Revision ID: e139b6e56ea6
Revises: 1d80c235f20a
Create Date: 2022-09-14 15:37:08.850923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e139b6e56ea6'
down_revision = '1d80c235f20a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group', sa.Column('description', sa.String(length=240), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('group', 'description')
    # ### end Alembic commands ###