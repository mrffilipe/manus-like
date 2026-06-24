"""Pydantic schemas for API."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


AgentMode = Literal["general", "marketing_consultant"]


class AttachmentInput(BaseModel):
    filename: str
    extracted_text: str
    content_type: str | None = None


class RunAgentRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    user_id: str | None = None
    conversation_id: uuid.UUID | None = None
    client_id: str | None = None
    agent_mode: AgentMode | None = None
    attachments: list[AttachmentInput] | None = None


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
    client_id: str | None = None
    agent_mode: str | None = None
    question: str | None = None
    options: list[str] | None = None
    error_message: str | None = None
    result: str | None = None


class ConversationSummary(BaseModel):
    id: uuid.UUID
    title: str | None
    client_id: str | None = None
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
    client_id: str | None = None
    messages: list[MessageResponse]


class DeleteConversationResponse(BaseModel):
    conversation_id: uuid.UUID
    deleted: bool


class AgentSettingsResponse(BaseModel):
    marketing_system_prompt: str


class UpdateAgentSettingsRequest(BaseModel):
    marketing_system_prompt: str = Field(..., min_length=1)


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


class ClientSummary(BaseModel):
    id: str
    slug: str
    name: str
    product: str
    description: str = ""
    resource_count: int = 0
    is_active: bool = True


class ClientListResponse(BaseModel):
    clients: list[ClientSummary]


class CreateClientRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    product: str = Field(..., min_length=1, max_length=256)
    description: str = ""
    slug: str | None = Field(default=None, max_length=64)
    profile: dict[str, Any] | None = None


class UpdateClientRequest(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    product: str | None = Field(default=None, max_length=256)
    description: str | None = None
    slug: str | None = Field(default=None, max_length=64)
    profile: dict[str, Any] | None = None
    is_active: bool | None = None


class ClientResourceResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    resource_type: Literal["file", "link", "prompt", "text"]
    category: str | None = None
    title: str
    content: str | None = None
    url: str | None = None
    extracted_text: str | None = None
    scraped_at: datetime | None = None
    metadata: dict[str, Any] | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime


class ClientDetailResponse(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    product: str
    description: str
    profile: dict[str, Any] | None = None
    is_active: bool
    resources: list[ClientResourceResponse]
    created_at: datetime
    updated_at: datetime


class CreateResourceRequest(BaseModel):
    resource_type: Literal["link", "prompt", "text"]
    title: str = Field(..., min_length=1, max_length=256)
    category: str | None = Field(default=None, max_length=128)
    content: str | None = None
    url: str | None = None
    metadata: dict[str, Any] | None = None


class UpdateResourceRequest(BaseModel):
    title: str | None = Field(default=None, max_length=256)
    category: str | None = Field(default=None, max_length=128)
    content: str | None = None
    url: str | None = None
    metadata: dict[str, Any] | None = None
    sort_order: int | None = None


class ClientArtifactResponse(BaseModel):
    id: uuid.UUID
    client_id: str
    artifact_type: str
    title: str
    content: str
    version: int
    created_at: datetime


class ClientArtifactListResponse(BaseModel):
    client_id: str
    artifacts: list[ClientArtifactResponse]


class UploadAttachmentResponse(BaseModel):
    filename: str
    extracted_text: str
    content_type: str | None = None
    char_count: int
