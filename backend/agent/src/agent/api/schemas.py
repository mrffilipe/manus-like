"""Pydantic schemas for API."""

import uuid
from typing import Literal

from pydantic import BaseModel, Field


class RunAgentRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    user_id: str | None = None
    conversation_id: uuid.UUID | None = None


class RunAgentResponse(BaseModel):
    execution_id: uuid.UUID
    status: Literal["Running", "WaitingHumanInput", "Completed", "Failed"]


class ContinueAgentRequest(BaseModel):
    answer: str = Field(..., min_length=1)


class AgentStatusResponse(BaseModel):
    execution_id: uuid.UUID
    status: Literal["Running", "WaitingHumanInput", "Completed", "Failed"]
    current_step: str | None = None
    goal: str
    question: str | None = None
    options: list[str] | None = None
    error_message: str | None = None
    result: str | None = None
