"""Pydantic schemas for API."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class RunAgentRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    user_id: str | None = None
    conversation_id: uuid.UUID | None = None


class RunAgentResponse(BaseModel):
    execution_id: uuid.UUID
    conversation_id: uuid.UUID
    status: Literal["Running", "WaitingHumanInput", "Completed", "Failed"]


class ContinueAgentRequest(BaseModel):
    answer: str = Field(..., min_length=1)


class AgentStatusResponse(BaseModel):
    execution_id: uuid.UUID
    conversation_id: uuid.UUID | None = None
    status: Literal["Running", "WaitingHumanInput", "Completed", "Failed"]
    current_step: str | None = None
    goal: str
    question: str | None = None
    options: list[str] | None = None
    error_message: str | None = None
    result: str | None = None


class ConversationSummary(BaseModel):
    id: uuid.UUID
    title: str | None
    updated_at: datetime
    last_message_preview: str | None = None


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    execution_id: uuid.UUID | None = None


class ConversationMessagesResponse(BaseModel):
    conversation_id: uuid.UUID
    messages: list[MessageResponse]


class DeleteConversationResponse(BaseModel):
    conversation_id: uuid.UUID
    deleted: bool


class ActivityEventResponse(BaseModel):
    id: uuid.UUID
    execution_id: uuid.UUID
    step: str
    kind: Literal["step_start", "step_done", "preview", "error"]
    title: str
    summary: str | None = None
    preview_type: Literal["text", "markdown", "search_results", "webpage", "screenshot"] | None = None
    preview_data: dict[str, Any] | None = None
    created_at: datetime


class ActivityListResponse(BaseModel):
    execution_id: uuid.UUID
    activities: list[ActivityEventResponse]
