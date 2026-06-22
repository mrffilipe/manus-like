"""Agent API routes."""

import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agent.api.schemas import (
    ActivityEventResponse,
    ActivityListResponse,
    AgentStatusResponse,
    ContinueAgentRequest,
    RunAgentRequest,
    RunAgentResponse,
)
from agent.persistence.database import get_session
from agent.persistence.models import ExecutionActivity, ExecutionStatus
from agent.persistence.repository import ExecutionRepository
from agent.queue.redis_queue import EVENTS_PREFIX, AgentJob, JobType, RedisQueue

router = APIRouter(prefix="/agent", tags=["agent"])

_queue: RedisQueue | None = None


async def get_queue() -> RedisQueue:
    global _queue
    if _queue is None:
        _queue = RedisQueue()
        await _queue.connect()
    return _queue


def _activity_to_response(activity: ExecutionActivity) -> ActivityEventResponse:
    return ActivityEventResponse(
        id=activity.id,
        execution_id=activity.execution_id,
        step=activity.step,
        kind=activity.kind,  # type: ignore[arg-type]
        title=activity.title,
        summary=activity.summary,
        preview_type=activity.preview_type,  # type: ignore[arg-type]
        preview_data=activity.preview_data,
        created_at=activity.created_at,
    )


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


@router.get("/activity/{execution_id}", response_model=ActivityListResponse)
async def get_activity(
    execution_id: uuid.UUID,
    since: uuid.UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> ActivityListResponse:
    repo = ExecutionRepository(session)
    execution = await repo.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    activities = await repo.list_activities(execution_id, since_id=since)
    return ActivityListResponse(
        execution_id=execution_id,
        activities=[_activity_to_response(activity) for activity in activities],
    )


@router.get("/events/{execution_id}")
async def stream_events(
    execution_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    repo = ExecutionRepository(session)
    execution = await repo.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    async def event_generator():
        queue = RedisQueue()
        await queue.connect()
        assert queue.redis is not None
        pubsub = queue.redis.pubsub()
        channel = f"{EVENTS_PREFIX}{execution_id}"
        await pubsub.subscribe(channel)
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=15.0)
                if message and message.get("type") == "message":
                    data = message.get("data")
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    yield f"data: {data}\n\n"
                    try:
                        payload = json.loads(data)
                        if payload.get("event") in {"completed", "failed", "waiting_human_input"}:
                            break
                    except json.JSONDecodeError:
                        pass
                else:
                    yield ": heartbeat\n\n"
                    await asyncio.sleep(0)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
            await queue.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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
