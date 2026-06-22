"""Data access layer."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent.persistence.models import (
    AgentExecution,
    Conversation,
    ExecutionActivity,
    ExecutionStatus,
    HumanInput,
    Message,
)


class ExecutionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_execution(
        self,
        goal: str,
        conversation_id: uuid.UUID | None = None,
        user_id: str | None = None,
    ) -> AgentExecution:
        if conversation_id is None:
            conversation = Conversation(user_id=user_id, title=goal[:120])
            self.session.add(conversation)
            await self.session.flush()
            conversation_id = conversation.id

        execution = AgentExecution(
            conversation_id=conversation_id,
            goal=goal,
            status=ExecutionStatus.RUNNING.value,
            current_step="planner",
        )
        self.session.add(execution)
        await self.session.flush()

        message = Message(
            conversation_id=conversation_id,
            execution_id=execution.id,
            role="user",
            content=goal,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def get_execution(self, execution_id: uuid.UUID) -> AgentExecution | None:
        result = await self.session.execute(
            select(AgentExecution).where(AgentExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def update_execution(
        self,
        execution_id: uuid.UUID,
        *,
        status: str | None = None,
        current_step: str | None = None,
        pending_question: str | None = None,
        pending_options: list | None = None,
        error_message: str | None = None,
        result: str | None = None,
        clear_pending: bool = False,
    ) -> AgentExecution | None:
        execution = await self.get_execution(execution_id)
        if execution is None:
            return None

        if status is not None:
            execution.status = status
        if current_step is not None:
            execution.current_step = current_step
        if pending_question is not None:
            execution.pending_question = pending_question
        if pending_options is not None:
            execution.pending_options = pending_options
        if error_message is not None:
            execution.error_message = error_message
        if result is not None:
            execution.result = result
        if clear_pending:
            execution.pending_question = None
            execution.pending_options = None

        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def add_message(
        self,
        execution_id: uuid.UUID,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> Message | None:
        execution = await self.get_execution(execution_id)
        if execution is None or execution.conversation_id is None:
            return None

        message = Message(
            conversation_id=execution.conversation_id,
            execution_id=execution_id,
            role=role,
            content=content,
            metadata_=metadata,
        )
        self.session.add(message)
        await self.session.commit()
        return message

    async def create_human_input(
        self,
        execution_id: uuid.UUID,
        question: str,
        options: list | None = None,
    ) -> HumanInput:
        human_input = HumanInput(
            execution_id=execution_id,
            question=question,
            options=options,
        )
        self.session.add(human_input)
        await self.session.commit()
        await self.session.refresh(human_input)
        return human_input

    async def resolve_human_input(
        self,
        execution_id: uuid.UUID,
        response: str,
    ) -> HumanInput | None:
        result = await self.session.execute(
            select(HumanInput)
            .where(HumanInput.execution_id == execution_id)
            .where(HumanInput.resolved_at.is_(None))
            .order_by(HumanInput.created_at.desc())
            .limit(1)
        )
        human_input = result.scalar_one_or_none()
        if human_input is None:
            return None

        human_input.response = response
        human_input.resolved_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(human_input)
        return human_input

    async def get_messages(self, execution_id: uuid.UUID) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.execution_id == execution_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def add_activity(
        self,
        execution_id: uuid.UUID,
        *,
        step: str,
        kind: str,
        title: str,
        summary: str | None = None,
        preview_type: str | None = None,
        preview_data: dict | None = None,
    ) -> ExecutionActivity:
        activity = ExecutionActivity(
            execution_id=execution_id,
            step=step,
            kind=kind,
            title=title,
            summary=summary,
            preview_type=preview_type,
            preview_data=preview_data,
        )
        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def get_activity(self, activity_id: uuid.UUID) -> ExecutionActivity | None:
        result = await self.session.execute(
            select(ExecutionActivity).where(ExecutionActivity.id == activity_id)
        )
        return result.scalar_one_or_none()

    async def list_activities(
        self,
        execution_id: uuid.UUID,
        since_id: uuid.UUID | None = None,
    ) -> list[ExecutionActivity]:
        query = (
            select(ExecutionActivity)
            .where(ExecutionActivity.execution_id == execution_id)
            .order_by(ExecutionActivity.created_at.asc())
        )
        if since_id is not None:
            ref = await self.get_activity(since_id)
            if ref is not None:
                query = query.where(ExecutionActivity.created_at > ref.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())
