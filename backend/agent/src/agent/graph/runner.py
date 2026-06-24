"""Graph execution service."""

import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from agent.activity.builders import build_fallback_activities
from agent.activity.recorder import ActivityRecorder
from agent.graph.builder import build_graph
from agent.graph.conversation_context import load_prior_messages
from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.gemini import get_llm_provider
from agent.logging_config import get_logger
from agent.marketing.agent_settings_service import AgentSettingsService
from agent.marketing.client_service import ClientService
from agent.marketing.persona import build_client_context_prompt
from agent.persistence.checkpoint import checkpoint_manager
from agent.persistence.models import ExecutionStatus
from agent.persistence.repository import ExecutionRepository
from agent.queue.redis_queue import RedisQueue

logger = get_logger(__name__)


class GraphRunner:
    def __init__(self) -> None:
        self.ctx = NodeContext(llm=get_llm_provider())
        self.checkpointer = None
        self.graph = None

    async def initialize(self) -> None:
        checkpointer = await checkpoint_manager.setup()
        self.checkpointer = checkpointer
        self.graph = build_graph(self.ctx, checkpointer)

    def _initial_state(
        self,
        execution_id: str,
        goal: str,
        *,
        prior_messages: list | None = None,
        conversation_id: str | None = None,
        agent_mode: str = "general",
        client_id: str | None = None,
        attachments: list | None = None,
        client_context: str = "",
        marketing_system_prompt: str = "",
    ) -> AgentState:
        history = list(prior_messages or [])
        return AgentState(
            goal=goal,
            messages=[*history, HumanMessage(content=goal)],
            current_step="planner",
            tool_calls=[],
            memory_context=[],
            execution_id=execution_id,
            conversation_id=conversation_id,
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
            agent_mode=agent_mode,  # type: ignore[typeddict-item]
            client_id=client_id,
            client_context=client_context,
            attachments=list(attachments or []),
            intake_complete=False,
            marketing_tool_results=[],
            marketing_system_prompt=marketing_system_prompt,
        )

    def _config(self, execution_id: str) -> dict:
        return {"configurable": {"thread_id": execution_id}}

    async def _on_node_update(
        self,
        recorder: ActivityRecorder,
        repo: ExecutionRepository,
        execution_id: uuid.UUID,
        node_name: str,
        update: dict[str, Any],
    ) -> None:
        current_step = update.get("current_step", node_name)
        await repo.update_execution(execution_id, current_step=current_step)

        events = list(update.get("activity_events") or [])
        if not events:
            events = build_fallback_activities(node_name, update)

        await recorder.record_events(events)

    async def _stream_graph(
        self,
        recorder: ActivityRecorder,
        repo: ExecutionRepository,
        execution_id: uuid.UUID,
        graph_input: Any,
        config: dict,
    ) -> dict[str, Any]:
        assert self.graph is not None

        async for chunk in self.graph.astream(graph_input, config=config, stream_mode="updates"):
            for node_name, update in chunk.items():
                await self._on_node_update(recorder, repo, execution_id, node_name, update)

        snapshot = await self.graph.aget_state(config)
        return dict(snapshot.values) if snapshot else {}

    async def run(
        self,
        repo: ExecutionRepository,
        execution_id: uuid.UUID,
        goal: str,
        human_response: str | None = None,
        resume: bool = False,
        queue: RedisQueue | None = None,
    ) -> dict[str, Any]:
        if self.graph is None:
            await self.initialize()

        assert self.graph is not None
        eid = str(execution_id)
        config = self._config(eid)
        recorder = ActivityRecorder(repo, queue, execution_id)
        self.ctx.activity = recorder

        try:
            if human_response is not None:
                result = await self._stream_graph(
                    recorder,
                    repo,
                    execution_id,
                    Command(resume=human_response),
                    config,
                )
            elif resume:
                result = await self._stream_graph(recorder, repo, execution_id, None, config)
            else:
                execution = await repo.get_execution(execution_id)
                prior_messages = []
                conversation_id: str | None = None
                if execution is not None and execution.conversation_id is not None:
                    conversation_id = str(execution.conversation_id)
                    prior_messages = await load_prior_messages(
                        repo,
                        execution.conversation_id,
                        execution_id,
                    )

                client_context = ""
                merged_attachments = list(execution.attachments or [])
                resolved_client_id = execution.client_id
                marketing_system_prompt = ""

                agent_mode = execution.agent_mode or "general"
                if agent_mode == "marketing_consultant":
                    settings_service = AgentSettingsService(repo.session)
                    marketing_system_prompt = await settings_service.get_marketing_system_prompt()

                if execution.client_id:
                    client_service = ClientService(repo.session)
                    resolved = await client_service.resolve_client_id(execution.client_id)
                    if resolved is not None:
                        resolved_client_id = str(resolved)
                        context_text, resource_attachments, link_count = (
                            await client_service.prepare_execution_context(resolved, scrape_links=True)
                        )
                        client_config = await client_service.build_client_config(resolved)
                        persona_ctx = build_client_context_prompt(client_config)
                        client_context = f"{persona_ctx}\n{context_text}".strip() if context_text else persona_ctx
                        merged_attachments = merged_attachments + resource_attachments
                        await recorder.record(
                            step="client_context",
                            kind="step_done",
                            title="Contexto do cliente carregado",
                            summary=f"{len(resource_attachments)} recursos, {link_count} links",
                            preview_type="markdown",
                            preview_data={"content": context_text[:3000] if context_text else "Sem contexto"},
                        )

                await recorder.record(
                    step="planner",
                    kind="step_start",
                    title="Iniciando execução",
                    summary=None,
                    preview_type="markdown",
                    preview_data={"content": goal},
                )
                result = await self._stream_graph(
                    recorder,
                    repo,
                    execution_id,
                    self._initial_state(
                        eid,
                        goal,
                        prior_messages=prior_messages,
                        conversation_id=conversation_id,
                        agent_mode=agent_mode,
                        client_id=resolved_client_id,
                        attachments=merged_attachments,
                        client_context=client_context,
                        marketing_system_prompt=marketing_system_prompt,
                    ),
                    config,
                )

            await self._sync_execution(repo, execution_id, result)
            return result

        except GraphInterrupt:
            snapshot = await self.graph.aget_state(config)
            state = dict(snapshot.values) if snapshot else {}
            await self._sync_execution(repo, execution_id, state, interrupted=True)
            return state

        except Exception as exc:
            await recorder.record(
                step="error",
                kind="error",
                title="Erro na execução",
                summary=str(exc),
                preview_type="text",
                preview_data={"content": str(exc)},
            )
            await repo.update_execution(
                execution_id,
                status=ExecutionStatus.FAILED.value,
                error_message=str(exc),
            )
            raise
        finally:
            self.ctx.activity = None

    async def _sync_execution(
        self,
        repo: ExecutionRepository,
        execution_id: uuid.UUID,
        state: dict,
        interrupted: bool = False,
    ) -> None:
        status = state.get("status", ExecutionStatus.RUNNING.value)
        assistant_content: str | None = None
        human_input_question: str | None = None
        human_input_options: list | None = None

        if interrupted or state.get("pending_question"):
            status = ExecutionStatus.WAITING_HUMAN_INPUT.value
            if state.get("pending_question"):
                human_input_question = state["pending_question"]
                human_input_options = state.get("pending_options")
                assistant_content = state["pending_question"]
        elif status == ExecutionStatus.COMPLETED.value:
            assistant_content = state.get("result")
            if not assistant_content and state.get("messages"):
                last = state["messages"][-1]
                assistant_content = last.content if hasattr(last, "content") else str(last)

            if state.get("client_id") and assistant_content:
                await repo.create_client_artifact(
                    client_id=state["client_id"],
                    artifact_type="deliverable",
                    title=state.get("goal", "Entregável")[:120],
                    content=assistant_content,
                    conversation_id=uuid.UUID(state["conversation_id"])
                    if state.get("conversation_id")
                    else None,
                    execution_id=execution_id,
                )

        await repo.finalize_execution(
            execution_id,
            status=status,
            current_step=state.get("current_step"),
            pending_question=state.get("pending_question"),
            pending_options=state.get("pending_options"),
            result=state.get("result"),
            assistant_content=assistant_content,
            clear_pending=status == ExecutionStatus.RUNNING.value,
            human_input_question=human_input_question,
            human_input_options=human_input_options,
        )
