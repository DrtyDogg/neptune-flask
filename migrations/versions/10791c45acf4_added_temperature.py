"""added temperature

Revision ID: 10791c45acf4
Revises: 51f0bbb37553
Create Date: 2019-01-18 15:32:51.389141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10791c45acf4'
down_revision = '51f0bbb37553'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('temperature',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('temp', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_temperature_timestamp'), 'temperature', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_temperature_timestamp'), table_name='temperature')
    op.drop_table('temperature')
    # ### end Alembic commands ###