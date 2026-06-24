"""Agent API routes."""

import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agent.api.schemas import (
    ActivityEventResponse,
    ActivityListResponse,
    AgentStatusResponse,
    ContinueAgentRequest,
    ConversationListResponse,
    ConversationMessagesResponse,
    ConversationSummary,
    DeleteConversationResponse,
    MessageResponse,
    RunAgentRequest,
    RunAgentResponse,
    UploadAttachmentResponse,
)
from agent.export.pdf_export import markdown_to_pdf_bytes
from agent.llm.gemini import get_llm_provider
from agent.persistence.database import get_session
from agent.persistence.models import ExecutionActivity, ExecutionStatus
from agent.persistence.repository import ExecutionRepository
from agent.queue.redis_queue import EVENTS_PREFIX, AgentJob, JobType, RedisQueue
from agent.tools.file_extractor import extract_text_from_bytes
from agent.tools.memory_client import MemoryClient

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


def _resolve_agent_mode(body: RunAgentRequest) -> str:
    if body.agent_mode:
        return body.agent_mode
    if body.client_id:
        return "marketing_consultant"
    return "general"


def _attachments_payload(body: RunAgentRequest) -> list[dict] | None:
    if not body.attachments:
        return None
    return [attachment.model_dump() for attachment in body.attachments]


async def _enqueue_execution(
    *,
    goal: str,
    repo: ExecutionRepository,
    queue: RedisQueue,
    conversation_id: uuid.UUID | None = None,
    user_id: str | None = None,
    client_id: str | None = None,
    agent_mode: str = "general",
    attachments: list[dict] | None = None,
) -> RunAgentResponse:
    execution = await repo.create_execution(
        goal=goal,
        conversation_id=conversation_id,
        user_id=user_id,
        agent_mode=agent_mode,
        client_id=client_id,
        attachments=attachments,
    )
    await queue.enqueue(AgentJob(execution_id=str(execution.id), job_type=JobType.RUN))
    return RunAgentResponse(
        execution_id=execution.id,
        conversation_id=execution.conversation_id,
        status="Running",
    )


@router.post("/attachments", response_model=list[UploadAttachmentResponse])
async def upload_attachments(
    files: list[UploadFile] = File(...),
) -> list[UploadAttachmentResponse]:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results: list[UploadAttachmentResponse] = []
    for upload in files:
        content = await upload.read()
        if not upload.filename:
            continue
        try:
            extracted = extract_text_from_bytes(upload.filename, content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        text = extracted.get("extracted_text", "")
        results.append(
            UploadAttachmentResponse(
                filename=upload.filename,
                extracted_text=text,
                content_type=extracted.get("content_type"),
                char_count=len(text),
            )
        )
    return results


@router.post("/run", response_model=RunAgentResponse)
async def run_agent(
    body: RunAgentRequest,
    session: AsyncSession = Depends(get_session),
    queue: RedisQueue = Depends(get_queue),
) -> RunAgentResponse:
    repo = ExecutionRepository(session)
    return await _enqueue_execution(
        goal=body.goal,
        repo=repo,
        queue=queue,
        conversation_id=body.conversation_id,
        user_id=body.user_id,
        client_id=body.client_id,
        agent_mode=_resolve_agent_mode(body),
        attachments=_attachments_payload(body),
    )


@router.post("/run/upload", response_model=RunAgentResponse)
async def run_agent_with_upload(
    goal: str = Form(...),
    conversation_id: uuid.UUID | None = Form(default=None),
    user_id: str | None = Form(default=None),
    client_id: str | None = Form(default=None),
    agent_mode: str | None = Form(default=None),
    files: list[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session),
    queue: RedisQueue = Depends(get_queue),
) -> RunAgentResponse:
    repo = ExecutionRepository(session)
    attachments: list[dict] = []
    for upload in files:
        content = await upload.read()
        if not upload.filename:
            continue
        try:
            extracted = extract_text_from_bytes(upload.filename, content)
            attachments.append(extracted)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    resolved_mode = agent_mode or ("marketing_consultant" if client_id else "general")
    return await _enqueue_execution(
        goal=goal,
        repo=repo,
        queue=queue,
        conversation_id=conversation_id,
        user_id=user_id,
        client_id=client_id,
        agent_mode=resolved_mode,
        attachments=attachments or None,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ConversationListResponse:
    repo = ExecutionRepository(session)
    items = await repo.list_conversations(user_id=user_id, limit=limit)
    return ConversationListResponse(
        conversations=[
            ConversationSummary(
                id=conversation.id,
                title=conversation.title,
                client_id=conversation.client_id,
                updated_at=conversation.updated_at,
                last_message_preview=(
                    preview[:120] + "…" if preview and len(preview) > 120 else preview
                ),
            )
            for conversation, preview in items
        ]
    )


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ConversationMessagesResponse:
    repo = ExecutionRepository(session)
    conversation = await repo.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await repo.get_conversation_messages(conversation_id)
    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        client_id=conversation.client_id,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
                execution_id=message.execution_id,
            )
            for message in messages
        ],
    )


@router.delete("/conversations/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    conversation_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> DeleteConversationResponse:
    repo = ExecutionRepository(session)
    execution_ids = await repo.delete_conversation(conversation_id)
    if execution_ids is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if execution_ids:
        memory = MemoryClient(get_llm_provider())
        try:
            await memory.delete_by_execution_ids(execution_ids)
        except Exception:
            pass

    return DeleteConversationResponse(conversation_id=conversation_id, deleted=True)


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
        conversation_id=execution.conversation_id,
        status=execution.status,
        current_step=execution.current_step,
        goal=execution.goal,
        client_id=execution.client_id,
        agent_mode=execution.agent_mode,
        question=execution.pending_question if execution.status == ExecutionStatus.WAITING_HUMAN_INPUT.value else None,
        options=execution.pending_options if execution.status == ExecutionStatus.WAITING_HUMAN_INPUT.value else None,
        error_message=execution.error_message,
        result=result,
    )


@router.get("/export/{execution_id}/pdf")
async def export_execution_pdf(
    execution_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Response:
    repo = ExecutionRepository(session)
    execution = await repo.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    content = execution.result
    if not content:
        messages = await repo.get_messages(execution_id)
        assistant_messages = [message for message in messages if message.role == "assistant"]
        if assistant_messages:
            content = assistant_messages[-1].content

    if not content:
        raise HTTPException(status_code=400, detail="No deliverable available for export")

    title = execution.goal[:80] if execution.goal else "Relatório"
    pdf_bytes = markdown_to_pdf_bytes(content, title=title)
    filename = f"relatorio-{execution_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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
    return RunAgentResponse(
        execution_id=execution_id,
        conversation_id=execution.conversation_id,
        status="Running",
    )


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

    await repo.add_message(execution_id, "user", body.answer)
    await repo.resolve_human_input(execution_id, body.answer)
    await repo.update_execution(execution_id, status=ExecutionStatus.RUNNING.value, clear_pending=True)
    await queue.enqueue(
        AgentJob(
            execution_id=str(execution_id),
            job_type=JobType.CONTINUE,
            human_response=body.answer,
        )
    )
    return RunAgentResponse(
        execution_id=execution_id,
        conversation_id=execution.conversation_id,
        status="Running",
    )
