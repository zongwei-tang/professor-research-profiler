"""add password_hash to users

Revision ID: 78afb7c7597b
Revises: 8e5b0e85e15f
Create Date: 2026-07-10 20:16:36.676590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78afb7c7597b'
down_revision: Union[str, Sequence[str], None] = '8e5b0e85e15f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(), nullable=True))
    op.execute("PRAGMA foreign_keys=ON")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_hash')
    op.execute("PRAGMA foreign_keys=ON")
