"""merge source_url migrations

Revision ID: 6a8ec83a9527
Revises: 62a48643fe65, 73ea07d54d0e
Create Date: 2025-06-13 14:06:20.698478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a8ec83a9527'
down_revision: Union[str, None] = ('62a48643fe65', '73ea07d54d0e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
