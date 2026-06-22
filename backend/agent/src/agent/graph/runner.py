"""Graph execution service."""

import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from agent.graph.builder import build_graph
from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.gemini import get_llm_provider
from agent.logging_config import get_logger
from agent.persistence.checkpoint import checkpoint_manager
from agent.persistence.models import ExecutionStatus
from agent.persistence.repository import ExecutionRepository

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

    def _initial_state(self, execution_id: str, goal: str) -> AgentState:
        return AgentState(
            goal=goal,
            messages=[HumanMessage(content=goal)],
            current_step="planner",
            tool_calls=[],
            memory_context=[],
            execution_id=execution_id,
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
        )

    def _config(self, execution_id: str) -> dict:
        return {"configurable": {"thread_id": execution_id}}

    async def run(
        self,
        repo: ExecutionRepository,
        execution_id: uuid.UUID,
        goal: str,
        human_response: str | None = None,
        resume: bool = False,
    ) -> dict[str, Any]:
        if self.graph is None:
            await self.initialize()

        assert self.graph is not None
        eid = str(execution_id)
        config = self._config(eid)

        try:
            if human_response is not None:
                result = await self.graph.ainvoke(
                    Command(resume=human_response),
                    config=config,
                )
            elif resume:
                result = await self.graph.ainvoke(None, config=config)
            else:
                result = await self.graph.ainvoke(
                    self._initial_state(eid, goal),
                    config=config,
                )

            await self._sync_execution(repo, execution_id, result)
            return result

        except GraphInterrupt:
            snapshot = await self.graph.aget_state(config)
            state = dict(snapshot.values) if snapshot else {}
            await self._sync_execution(repo, execution_id, state, interrupted=True)
            return state

        except Exception as exc:
            await repo.update_execution(
                execution_id,
                status=ExecutionStatus.FAILED.value,
                error_message=str(exc),
            )
            raise

    async def _sync_execution(
        self,
        repo: ExecutionRepository,
        execution_id: uuid.UUID,
        state: dict,
        interrupted: bool = False,
    ) -> None:
        status = state.get("status", ExecutionStatus.RUNNING.value)
        if interrupted or state.get("pending_question"):
            status = ExecutionStatus.WAITING_HUMAN_INPUT.value
            if state.get("pending_question"):
                await repo.create_human_input(
                    execution_id,
                    state["pending_question"],
                    state.get("pending_options"),
                )

        await repo.update_execution(
            execution_id,
            status=status,
            current_step=state.get("current_step"),
            pending_question=state.get("pending_question"),
            pending_options=state.get("pending_options"),
            result=state.get("result"),
            clear_pending=status == ExecutionStatus.RUNNING.value,
        )

        if state.get("messages"):
            last = state["messages"][-1]
            content = last.content if hasattr(last, "content") else str(last)
            message_role = "assistant"
            if status == ExecutionStatus.COMPLETED.value and state.get("result"):
                content = state["result"]
            await repo.add_message(execution_id, message_role, content)
