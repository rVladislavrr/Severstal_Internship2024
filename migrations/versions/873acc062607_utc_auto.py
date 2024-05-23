"""utc_auto

Revision ID: 873acc062607
Revises: db0a9d47c5c6
Create Date: 2024-05-21 20:42:31.908085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '873acc062607'
down_revision: Union[str, None] = 'db0a9d47c5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stock', 'data_add')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stock', sa.Column('data_add', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("timezone('utc'::text, now())"), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
