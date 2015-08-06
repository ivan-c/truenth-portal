"""empty message

Revision ID: 4364a2938db0
Revises: 239ed71a3de6
Create Date: 2015-08-05 18:05:59.063534

"""

# revision identifiers, used by Alembic.
revision = '4364a2938db0'
down_revision = '239ed71a3de6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('codeable_concepts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=80), nullable=False),
    sa.Column('display', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('value_quantities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=80), nullable=True),
    sa.Column('units', sa.String(length=80), nullable=True),
    sa.Column('system', sa.String(length=255), nullable=True),
    sa.Column('code', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('observations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('issued', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=80), nullable=True),
    sa.Column('codeable_concept_id', sa.Integer(), nullable=True),
    sa.Column('value_quantity_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['codeable_concept_id'], ['codeable_concepts.id'], ),
    sa.ForeignKeyConstraint(['value_quantity_id'], ['value_quantities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_observations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('observation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['observation_id'], ['observations.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_observations')
    op.drop_table('observations')
    op.drop_table('value_quantities')
    op.drop_table('codeable_concepts')
    ### end Alembic commands ###
