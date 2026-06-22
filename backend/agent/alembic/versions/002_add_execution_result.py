"""Add result column to agent_executions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agent_executions", sa.Column("result", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("agent_executions", "result")
