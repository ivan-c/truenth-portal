"""empty message

Revision ID: 8062d67a91e0
Revises: 9294a022188d
Create Date: 2016-08-15 11:55:22.406887

"""

# revision identifiers, used by Alembic.
revision = '8062d67a91e0'
down_revision = '9294a022188d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('rank_per_intervention', 'access_strategies', [
                                'intervention_id', 'rank'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('rank_per_intervention',
                       'access_strategies', type_='unique')
    ### end Alembic commands ###
