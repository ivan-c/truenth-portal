"""empty message

Revision ID: feb22883a500
Revises: 3d317a184862
Create Date: 2017-04-05 11:00:47.310296

"""

# revision identifiers, used by Alembic.
revision = 'feb22883a500'
down_revision = '3d317a184862'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


def upgrade():
    # before adding null constraint - make any existing null emails
    # match the user id.
    conn = op.get_bind()
    result = conn.execute(text("""SELECT id FROM users WHERE email is null"""))
    results = result.fetchall()
    for r in results:
        conn.execute(text("""UPDATE users SET email=:id WHERE id=:id"""),
                     id=r[0])
    op.alter_column('users', 'email',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
                    existing_type=sa.VARCHAR(length=120),
                    nullable=True)
    # ### end Alembic commands ###
