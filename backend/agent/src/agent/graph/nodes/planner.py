"""Planner node."""

from langchain_core.messages import AIMessage

from agent.graph.conversation_context import format_conversation_history
from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message


async def planner_node(state: AgentState, ctx: NodeContext) -> dict:
    memory_snippets = "\n".join(state.get("memory_context", []))
    conversation_history = format_conversation_history(state.get("messages", []), state["goal"])
    history_section = f"\n{conversation_history}\n" if conversation_history else ""
    prompt = f"""You are an autonomous agent planner.
Goal: {state['goal']}
Current iteration: {state.get('iteration', 0)}
{history_section}Memory context:
{memory_snippets or 'None'}

Create a concise plan for the next actions. If the conversation history already contains
the information needed to answer the current goal, prefer using critic or tools instead of
re-fetching the same website or repeating prior research.

Decide which capability to use next:
- research: web search
- browser: navigate websites
- tools: execute generic tool calls
- memory: store or recall facts
- critic: evaluate progress

Respond with a short plan and end with NEXT_ACTION: <action> where action is one of research, browser, tools, memory, critic.
"""

    response = await ctx.llm.chat([Message(role="user", content=prompt)])
    plan = response.content
    next_action = "research"
    for line in plan.splitlines():
        if "NEXT_ACTION:" in line:
            action = line.split("NEXT_ACTION:")[-1].strip().lower()
            if action in {"research", "browser", "tools", "memory", "critic"}:
                next_action = action
            break

    return {
        "plan": plan,
        "current_step": "planner",
        "next_route": next_action,
        "iteration": state.get("iteration", 0) + 1,
        "messages": [AIMessage(content=f"[Planner] {plan}")],
        "activity_events": [
            {
                "step": "planner",
                "kind": "step_done",
                "title": "Planejamento concluído",
                "summary": None,
                "preview_type": "markdown",
                "preview_data": {"content": plan[:3000]},
            }
        ],
    }
