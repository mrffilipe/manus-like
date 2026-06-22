"""Critic node - evaluates progress and routes next step."""

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message

_SECTION_HEADERS = ("DECISION:", "QUESTION:", "OPTIONS:", "SUMMARY:", "DELIVERABLE:")


def _parse_deliverable(text: str) -> str | None:
    lines = text.splitlines()
    deliverable_lines: list[str] = []
    in_deliverable = False

    for line in lines:
        upper = line.upper()
        if upper.startswith("DELIVERABLE:"):
            in_deliverable = True
            rest = line.split(":", 1)[1].strip()
            if rest:
                deliverable_lines.append(rest)
            continue
        if in_deliverable and any(upper.startswith(header) for header in _SECTION_HEADERS if header != "DELIVERABLE:"):
            in_deliverable = False
            continue
        if in_deliverable:
            deliverable_lines.append(line)

    deliverable = "\n".join(deliverable_lines).strip()
    return deliverable or None


async def critic_node(state: AgentState, ctx: NodeContext) -> dict:
    context = "\n".join(
        msg.content for msg in state.get("messages", []) if hasattr(msg, "content")
    )
    prompt = f"""You are a critic evaluating an autonomous agent.

Goal: {state['goal']}
Iteration: {state.get('iteration', 0)}
Max iterations: 10
Work so far:
{context}

Decide one of:
- DONE: goal is sufficiently addressed
- CONTINUE: more work needed
- HUMAN: critical ambiguity requires human input (provide question and options)

When DECISION is DONE, you MUST include a DELIVERABLE section with the complete
user-facing answer in the format requested by the goal (e.g. markdown table).
Do not only describe what was done — include the actual content.

Format:
DECISION: <DONE|CONTINUE|HUMAN>
QUESTION: <only if HUMAN>
OPTIONS: <comma-separated options, only if HUMAN>
DELIVERABLE: <only if DONE — full final answer for the user>
SUMMARY: <brief summary of current progress>"""

    response = await ctx.llm.chat([Message(role="user", content=prompt)])
    text = response.content

    decision = "CONTINUE"
    question = None
    options: list[str] | None = None
    deliverable = _parse_deliverable(text)

    for line in text.splitlines():
        upper = line.upper()
        if upper.startswith("DECISION:"):
            decision = line.split(":", 1)[1].strip().upper()
        elif upper.startswith("QUESTION:"):
            question = line.split(":", 1)[1].strip()
        elif upper.startswith("OPTIONS:"):
            raw = line.split(":", 1)[1].strip()
            options = [o.strip() for o in raw.split(",") if o.strip()]

    if state.get("iteration", 0) >= 10:
        decision = "DONE"

    if decision == "HUMAN" and question:
        return {
            "current_step": "critic",
            "needs_human": True,
            "pending_question": question,
            "pending_options": options,
            "next_route": "human",
            "status": "WaitingHumanInput",
            "messages": [AIMessage(content=f"[Critic] Needs human input: {question}")],
        }

    if decision == "DONE":
        return {
            "current_step": "critic",
            "needs_human": False,
            "next_route": "end",
            "status": "Completed",
            "result": deliverable,
            "messages": [AIMessage(content=deliverable or f"[Critic] Completed.\n{text}")],
        }

    return {
        "current_step": "critic",
        "needs_human": False,
        "next_route": "planner",
        "status": "Running",
        "iteration": state.get("iteration", 0) + 1,
        "messages": [AIMessage(content=f"[Critic] Continue.\n{text}")],
    }
