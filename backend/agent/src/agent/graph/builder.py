"""LangGraph builder."""

from functools import partial
from typing import Any

from langgraph.graph import END, StateGraph

from agent.config import settings
from agent.graph.deps import NodeContext
from agent.graph.nodes.browser import browser_node
from agent.graph.nodes.critic import critic_node
from agent.graph.nodes.human_input import human_input_node
from agent.graph.nodes.memory import memory_node
from agent.graph.nodes.planner import planner_node
from agent.graph.nodes.research import research_node
from agent.graph.nodes.tool_execution import tool_execution_node
from agent.graph.state import AgentState
from agent.llm.gemini import get_llm_provider


def _wrap(fn, ctx: NodeContext):
    async def wrapped(state: AgentState) -> dict:
        return await fn(state, ctx)

    return wrapped


def route_from_planner(state: AgentState) -> str:
    return state.get("next_route", "research")


def route_from_step(state: AgentState) -> str:
    return state.get("next_route", "memory")


def route_from_critic(state: AgentState) -> str:
    route = state.get("next_route", "planner")
    if route == "end":
        return END
    return route


def build_graph(ctx: NodeContext | None = None, checkpointer: Any = None):
    if ctx is None:
        ctx = NodeContext(llm=get_llm_provider())

    graph = StateGraph(AgentState)

    graph.add_node("planner", _wrap(planner_node, ctx))
    graph.add_node("research", _wrap(research_node, ctx))
    graph.add_node("browser", _wrap(browser_node, ctx))
    graph.add_node("tool_execution", _wrap(tool_execution_node, ctx))
    graph.add_node("memory", _wrap(memory_node, ctx))
    graph.add_node("critic", _wrap(critic_node, ctx))
    graph.add_node("human_input", _wrap(human_input_node, ctx))

    graph.set_entry_point("planner")

    graph.add_conditional_edges("planner", route_from_planner, {
        "research": "research",
        "browser": "browser",
        "tools": "tool_execution",
        "memory": "memory",
        "critic": "critic",
    })

    graph.add_edge("research", "browser")
    graph.add_edge("browser", "tool_execution")
    graph.add_edge("tool_execution", "memory")
    graph.add_edge("memory", "critic")

    graph.add_conditional_edges("critic", route_from_critic, {
        "planner": "planner",
        "human": "human_input",
        END: END,
    })

    graph.add_edge("human_input", "planner")

    return graph.compile(checkpointer=checkpointer, interrupt_before=[])
