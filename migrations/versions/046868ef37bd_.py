"""empty message

Revision ID: 046868ef37bd
Revises: fb44c8a04584
Create Date: 2024-11-13 17:16:24.328819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '046868ef37bd'
down_revision = 'fb44c8a04584'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_super_admin', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('roles')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('is_super_admin', sa.BOOLEAN(), nullable=True),
    sa.Column('is_admin', sa.BOOLEAN(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('role')
    # ### end Alembic commands ###
