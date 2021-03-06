"""empty message

Revision ID: af193c376724
Revises: 1a0225311859
Create Date: 2017-06-28 12:21:45.840441

"""

# revision identifiers, used by Alembic.
revision = 'af193c376724'
down_revision = '1a0225311859'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tou', sa.Column(
        'organization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tou', 'organizations',
                          ['organization_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tou', type_='foreignkey')
    op.drop_column('tou', 'organization_id')
    # ### end Alembic commands ###
