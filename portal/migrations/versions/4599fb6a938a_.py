"""empty message

Revision ID: 4599fb6a938a
Revises: 2439eea5b23c
Create Date: 2016-01-20 19:39:31.855502

"""

# revision identifiers, used by Alembic.
revision = '4599fb6a938a'
down_revision = '2439eea5b23c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relationships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_relationships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('other_user_id', sa.Integer(), nullable=True),
    sa.Column('relationship_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['other_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['relationship_id'], ['relationships.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'other_user_id', 'relationship_id', name='_user_relationship')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_relationships')
    op.drop_table('relationships')
    ### end Alembic commands ###