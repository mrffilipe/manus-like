"""Helpers for loading and formatting conversation history."""

import uuid

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agent.persistence.models import Message
from agent.persistence.repository import ExecutionRepository


def message_to_langchain(message: Message) -> BaseMessage | None:
    if message.role == "user":
        return HumanMessage(content=message.content)
    if message.role == "assistant":
        return AIMessage(content=message.content)
    return None


def build_prior_messages(messages: list[Message], current_execution_id: uuid.UUID) -> list[BaseMessage]:
    prior: list[BaseMessage] = []
    for message in messages:
        if message.execution_id == current_execution_id:
            continue
        langchain_message = message_to_langchain(message)
        if langchain_message is not None:
            prior.append(langchain_message)
    return prior


async def load_prior_messages(
    repo: ExecutionRepository,
    conversation_id: uuid.UUID,
    current_execution_id: uuid.UUID,
) -> list[BaseMessage]:
    messages = await repo.get_conversation_messages(conversation_id)
    return build_prior_messages(messages, current_execution_id)


def format_conversation_history(messages: list[BaseMessage], goal: str) -> str:
    if not messages:
        return ""

    lines: list[str] = []
    for message in messages:
        content = message.content if hasattr(message, "content") else str(message)
        if isinstance(message, HumanMessage):
            if content == goal:
                continue
            lines.append(f"User: {content}")
        elif isinstance(message, AIMessage):
            lines.append(f"Assistant: {content}")

    if not lines:
        return ""

    return "Conversation so far:\n" + "\n".join(lines) + f"\nUser (current goal): {goal}"
