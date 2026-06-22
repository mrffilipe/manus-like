"""Agent API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from agent.api.schemas import (
    AgentStatusResponse,
    ContinueAgentRequest,
    RunAgentRequest,
    RunAgentResponse,
)
from agent.persistence.database import get_session
from agent.persistence.models import ExecutionStatus
from agent.persistence.repository import ExecutionRepository
from agent.queue.redis_queue import AgentJob, JobType, RedisQueue

router = APIRouter(prefix="/agent", tags=["agent"])

_queue: RedisQueue | None = None


async def get_queue() -> RedisQueue:
    global _queue
    if _queue is None:
        _queue = RedisQueue()
        await _queue.connect()
    return _queue


@router.post("/run", response_model=RunAgentResponse)
async def run_agent(
    body: RunAgentRequest,
    session: AsyncSession = Depends(get_session),
    queue: RedisQueue = Depends(get_queue),
) -> RunAgentResponse:
    repo = ExecutionRepository(session)
    execution = await repo.create_execution(
        goal=body.goal,
        conversation_id=body.conversation_id,
        user_id=body.user_id,
    )
    await queue.enqueue(AgentJob(execution_id=str(execution.id), job_type=JobType.RUN))
    return RunAgentResponse(execution_id=execution.id, status="Running")


@router.get("/status/{execution_id}", response_model=AgentStatusResponse)
async def get_status(
    execution_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> AgentStatusResponse:
    repo = ExecutionRepository(session)
    execution = await repo.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    result = execution.result
    if result is None and execution.status == ExecutionStatus.COMPLETED.value:
        messages = await repo.get_messages(execution_id)
        assistant_messages = [message for message in messages if message.role == "assistant"]
        if assistant_messages:
            result = assistant_messages[-1].content

    return AgentStatusResponse(
        execution_id=execution.id,
        status=execution.status,
        current_step=execution.current_step,
        goal=execution.goal,
        question=execution.pending_question if execution.status == ExecutionStatus.WAITING_HUMAN_INPUT.value else None,
        options=execution.pending_options if execution.status == ExecutionStatus.WAITING_HUMAN_INPUT.value else None,
        error_message=execution.error_message,
        result=result,
    )


@router.post("/resume/{execution_id}", response_model=RunAgentResponse)
async def resume_agent(
    execution_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    queue: RedisQueue = Depends(get_queue),
) -> RunAgentResponse:
    repo = ExecutionRepository(session)
    execution = await repo.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status not in {
        ExecutionStatus.RUNNING.value,
        ExecutionStatus.WAITING_HUMAN_INPUT.value,
        ExecutionStatus.FAILED.value,
    }:
        raise HTTPException(status_code=400, detail=f"Cannot resume execution in status {execution.status}")

    await repo.update_execution(execution_id, status=ExecutionStatus.RUNNING.value, clear_pending=True)
    await queue.enqueue(AgentJob(execution_id=str(execution_id), job_type=JobType.RESUME))
    return RunAgentResponse(execution_id=execution_id, status="Running")


@router.post("/continue/{execution_id}", response_model=RunAgentResponse)
async def continue_agent(
    execution_id: uuid.UUID,
    body: ContinueAgentRequest,
    session: AsyncSession = Depends(get_session),
    queue: RedisQueue = Depends(get_queue),
) -> RunAgentResponse:
    repo = ExecutionRepository(session)
    execution = await repo.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status != ExecutionStatus.WAITING_HUMAN_INPUT.value:
        raise HTTPException(status_code=400, detail="Execution is not waiting for human input")

    await repo.resolve_human_input(execution_id, body.answer)
    await repo.update_execution(execution_id, status=ExecutionStatus.RUNNING.value, clear_pending=True)
    await queue.enqueue(
        AgentJob(
            execution_id=str(execution_id),
            job_type=JobType.CONTINUE,
            human_response=body.answer,
        )
    )
    return RunAgentResponse(execution_id=execution_id, status="Running")
