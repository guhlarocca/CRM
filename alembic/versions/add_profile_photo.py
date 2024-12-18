"""Add profile_photo column to time table

Revision ID: add_profile_photo
Revises: 
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_profile_photo'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('time', sa.Column('profile_photo', sa.String(length=255), nullable=True, server_default='default_profile.png'))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('time', 'profile_photo')
    # ### end Alembic commands ###
