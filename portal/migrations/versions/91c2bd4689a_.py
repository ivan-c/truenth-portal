"""empty message

Revision ID: 91c2bd4689a
Revises: 4456ad5faf86
Create Date: 2015-09-17 14:33:02.014680

"""

# revision identifiers, used by Alembic.
revision = '91c2bd4689a'
down_revision = '4456ad5faf86'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column(
        'callback_url', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clients', 'callback_url')
    ### end Alembic commands ###
