"""LangGraph agent state."""

import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    goal: str
    messages: Annotated[list[BaseMessage], operator.add]
    current_step: str
    tool_calls: list[dict]
    memory_context: list[str]
    execution_id: str
    conversation_id: str | None
    status: Literal["Running", "WaitingHumanInput", "Completed", "Failed"]
    pending_question: str | None
    pending_options: list[str] | None
    iteration: int
    next_route: str
    plan: str
    research_results: list[dict]
    browser_results: list[dict]
    needs_human: bool
    human_response: str | None
    result: str | None
    activity_events: Annotated[list[dict], operator.add]
