"""Planner node."""

from langchain_core.messages import AIMessage

from agent.graph.conversation_context import format_conversation_history
from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message
from agent.marketing.metrics_auto_detector import collect_marketing_context, context_has_marketing_metrics
from agent.marketing.persona import resolve_marketing_system_prompt


def _attachments_context(attachments: list[dict]) -> str:
    if not attachments:
        return ""
    parts = ["\nAnexos do usuário:"]
    for attachment in attachments:
        filename = attachment.get("filename", "arquivo")
        text = attachment.get("extracted_text", "")
        preview = text[:4000] + ("…" if len(text) > 4000 else "")
        parts.append(f"\n### {filename}\n{preview}")
    return "\n".join(parts)


async def planner_node(state: AgentState, ctx: NodeContext) -> dict:
    memory_snippets = "\n".join(state.get("memory_context", []))
    conversation_history = format_conversation_history(state.get("messages", []), state["goal"])
    history_section = f"\n{conversation_history}\n" if conversation_history else ""
    attachments_section = _attachments_context(state.get("attachments", []))
    marketing_section = ""
    if state.get("agent_mode") == "marketing_consultant":
        persona = resolve_marketing_system_prompt(state.get("marketing_system_prompt"))
        marketing_section = (
            f"\n{persona}\n"
            f"{state.get('client_context', '')}\n"
            "Priorize coletar contexto antes de recomendar. Use ferramentas de marketing quando houver métricas ou copies.\n"
        )

    prompt = f"""You are an autonomous agent planner.
{marketing_section}
Goal: {state['goal']}
Current iteration: {state.get('iteration', 0)}
Client: {state.get('client_id') or 'não definido'}
{history_section}{attachments_section}
Memory context:
{memory_snippets or 'None'}

Create a concise plan for the next actions. If the conversation history already contains
the information needed to answer the current goal, prefer using tools or critic instead of
re-fetching the same website or repeating prior research.
If the history contains funnel metrics, campaign numbers, or comparisons (envios, abertura, CTR, leads),
use NEXT_ACTION: tools (not critic directly) so metrics are processed for automatic charts.

Decide which capability to use next:
- research: web search
- browser: navigate websites (LPs, sites institucionais)
- tools: execute tools (marketing analysis, audits, prompt generation)
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

    if (
        state.get("agent_mode") == "marketing_consultant"
        and next_action == "critic"
        and not state.get("marketing_tool_results")
        and context_has_marketing_metrics(collect_marketing_context(state))
    ):
        next_action = "tools"

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
