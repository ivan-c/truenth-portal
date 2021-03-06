from alembic import op
import sqlalchemy as sa

"""empty message

Revision ID: 458dd2fc1172
Revises: 8ecdd6381235
Create Date: 2017-12-21 16:38:49.659073

"""

# revision identifiers, used by Alembic.
revision = '458dd2fc1172'
down_revision = '8ecdd6381235'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'user_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'notification_id',
                            name='_user_notification')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_notifications')
    op.drop_table('notifications')
    # ### end Alembic commands ###
