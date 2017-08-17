"""empty message

Revision ID: 66d8893fe442
Revises: 936971a9b55d
Create Date: 2016-05-17 17:05:18.996909

"""

# revision identifiers, used by Alembic.
revision = '66d8893fe442'
down_revision = '936971a9b55d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('audit',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.Column('version', sa.Text(), nullable=False),
                    sa.Column('comment', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('procedures',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('start_time', sa.DateTime(), nullable=False),
                    sa.Column('end_time', sa.DateTime(), nullable=True),
                    sa.Column('code_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('audit_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['audit_id'], ['audit.id'], ),
                    sa.ForeignKeyConstraint(
                        ['code_id'], ['codeable_concepts.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column(u'observations', sa.Column('audit_id', sa.Integer()))
    op.create_foreign_key('observations_audit_fk',
                          'observations', 'audit', ['audit_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('observations_audit_fk',
                       'observations', type_='foreignkey')
    op.drop_column(u'observations', 'audit_id')
    op.drop_table('procedures')
    op.drop_table('audit')
    ### end Alembic commands ###
