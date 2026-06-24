"""Tests for execution repository client inheritance."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from agent.persistence.models import Conversation
from agent.persistence.repository import ExecutionRepository


@pytest.mark.asyncio
async def test_create_execution_inherits_conversation_client():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    repo = ExecutionRepository(session)
    client_id = str(uuid.uuid4())
    conversation_id = uuid.uuid4()
    conversation = Conversation(id=conversation_id, client_id=client_id, title="Test")

    repo.get_conversation = AsyncMock(return_value=conversation)  # type: ignore[method-assign]

    execution = await repo.create_execution(
        goal="Follow-up",
        conversation_id=conversation_id,
    )

    assert execution.agent_mode == "marketing_consultant"
    assert execution.client_id == client_id
