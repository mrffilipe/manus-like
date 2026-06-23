"""Tests for conversation history loading and formatting."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agent.graph.conversation_context import (
    build_prior_messages,
    format_conversation_history,
    load_prior_messages,
)
from agent.graph.nodes.planner import planner_node
from agent.graph.state import AgentState
from agent.persistence.models import Message


def _message(
    *,
    role: str,
    content: str,
    execution_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Message:
    return Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        execution_id=execution_id,
        role=role,
        content=content,
        created_at=datetime.now(timezone.utc),
    )


def test_build_prior_messages_excludes_current_execution():
    conversation_id = uuid.uuid4()
    exec_1 = uuid.uuid4()
    exec_2 = uuid.uuid4()

    messages = [
        _message(role="user", content="First question", execution_id=exec_1, conversation_id=conversation_id),
        _message(
            role="assistant",
            content="First answer",
            execution_id=exec_1,
            conversation_id=conversation_id,
        ),
        _message(role="user", content="Follow-up", execution_id=exec_2, conversation_id=conversation_id),
    ]

    prior = build_prior_messages(messages, exec_2)

    assert len(prior) == 2
    assert isinstance(prior[0], HumanMessage)
    assert prior[0].content == "First question"
    assert isinstance(prior[1], AIMessage)
    assert prior[1].content == "First answer"


def test_format_conversation_history_includes_prior_turns():
    messages = [
        HumanMessage(content="List services from the website"),
        AIMessage(content="Main services: blinds, consulting, B2B"),
        HumanMessage(content="Which do you recommend?"),
    ]

    formatted = format_conversation_history(messages, "Which do you recommend?")

    assert "Conversation so far:" in formatted
    assert "List services from the website" in formatted
    assert "Main services: blinds, consulting, B2B" in formatted
    assert "User (current goal): Which do you recommend?" in formatted


@pytest.mark.asyncio
async def test_load_prior_messages_fetches_from_repository():
    conversation_id = uuid.uuid4()
    execution_id = uuid.uuid4()
    prior = _message(
        role="assistant",
        content="Prior answer",
        execution_id=uuid.uuid4(),
        conversation_id=conversation_id,
    )

    repo = AsyncMock()
    repo.get_conversation_messages = AsyncMock(return_value=[prior])

    result = await load_prior_messages(repo, conversation_id, execution_id)

    repo.get_conversation_messages.assert_awaited_once_with(conversation_id)
    assert len(result) == 1
    assert isinstance(result[0], AIMessage)
    assert result[0].content == "Prior answer"


@pytest.mark.asyncio
async def test_planner_prompt_includes_conversation_history():
    captured_prompts: list[str] = []

    async def fake_chat(messages, tools=None):
        captured_prompts.append(messages[0].content)
        from agent.llm.base import LLMResponse

        return LLMResponse(content="Plan\nNEXT_ACTION: critic")

    ctx = MagicMock()
    ctx.llm.chat = fake_chat

    state = AgentState(
        goal="Which service do you recommend?",
        messages=[
            HumanMessage(content="List DM2 services"),
            AIMessage(content="Services: blinds, consulting, B2B, logistics"),
            HumanMessage(content="Which service do you recommend?"),
        ],
        current_step="planner",
        tool_calls=[],
        memory_context=[],
        execution_id="exec-2",
        conversation_id="conv-1",
        status="Running",
        pending_question=None,
        pending_options=None,
        iteration=0,
        next_route="research",
        plan="",
        research_results=[],
        browser_results=[],
        needs_human=False,
        human_response=None,
        result=None,
        activity_events=[],
    )

    await planner_node(state, ctx)

    assert captured_prompts
    assert "Conversation so far:" in captured_prompts[0]
    assert "List DM2 services" in captured_prompts[0]
    assert "Services: blinds, consulting, B2B, logistics" in captured_prompts[0]


@pytest.mark.asyncio
async def test_finalize_execution_persists_status_and_assistant_message():
    from agent.persistence.repository import ExecutionRepository

    conversation_id = uuid.uuid4()
    execution_id = uuid.uuid4()

    execution = MagicMock()
    execution.id = execution_id
    execution.conversation_id = conversation_id
    execution.status = "Running"

    session = AsyncMock()
    repo = ExecutionRepository(session)
    repo.get_execution = AsyncMock(return_value=execution)
    repo._touch_conversation = AsyncMock()

    result = await repo.finalize_execution(
        execution_id,
        status="Completed",
        result="Recommended service: consulting",
        assistant_content="Recommended service: consulting",
    )

    assert result is execution
    assert execution.status == "Completed"
    assert execution.result == "Recommended service: consulting"
    session.add.assert_called()
    session.commit.assert_awaited_once()
