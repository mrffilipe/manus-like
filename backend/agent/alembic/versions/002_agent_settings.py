"""Agent settings table with default marketing persona seed."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from agent.marketing.persona import DEFAULT_MARKETING_SYSTEM_PROMPT

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MARKETING_SYSTEM_PROMPT_KEY = "marketing_system_prompt"


def upgrade() -> None:
    op.create_table(
        "agent_settings",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )

    settings_table = sa.table(
        "agent_settings",
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
    )
    op.bulk_insert(
        settings_table,
        [{"key": MARKETING_SYSTEM_PROMPT_KEY, "value": DEFAULT_MARKETING_SYSTEM_PROMPT}],
    )


def downgrade() -> None:
    op.drop_table("agent_settings")
