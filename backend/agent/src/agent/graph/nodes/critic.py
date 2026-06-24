"""Critic node - evaluates progress and routes next step."""

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message
from agent.marketing.intake import evaluate_intake
from agent.marketing.persona import resolve_marketing_system_prompt
from agent.marketing.report_formatter import merge_deliverable_with_visuals
from agent.marketing.metrics_auto_detector import (
    auto_detect_marketing_tool_results,
    collect_marketing_context,
    merge_tool_results,
)

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


def _messages_text(state: AgentState) -> str:
    return "\n".join(
        msg.content for msg in state.get("messages", []) if hasattr(msg, "content")
    )


async def critic_node(state: AgentState, ctx: NodeContext) -> dict:
    context = _messages_text(state)
    marketing_mode = state.get("agent_mode") == "marketing_consultant"
    intake_section = ""
    force_human = False
    forced_question: str | None = None
    forced_options: list[str] | None = None

    if marketing_mode:
        intake = evaluate_intake(
            goal=state["goal"],
            messages_text=context,
            attachments=state.get("attachments", []),
            client_id=state.get("client_id"),
        )
        if not intake.complete and intake.next_question:
            force_human = True
            forced_question = intake.next_question
            forced_options = intake.next_options
            intake_section = (
                f"\nIntake incompleto. Itens faltando: {', '.join(intake.missing) or intake.next_key}.\n"
                "Se faltar contexto crítico, use DECISION: HUMAN para solicitar dados antes de concluir.\n"
            )

    tool_results = state.get("marketing_tool_results", [])
    tool_section = ""
    if tool_results:
        tool_section = "\nResultados de ferramentas de marketing:\n" + "\n".join(
            str(item) for item in tool_results[-5:]
        )

    persona = (
        resolve_marketing_system_prompt(state.get("marketing_system_prompt"))
        if marketing_mode
        else "You are a critic evaluating an autonomous agent."
    )
    deliverable_hint = (
        "alertas críticos, hipóteses ranqueadas por impacto, recomendações priorizadas e próximos passos "
        "(KPIs, funis comparativos e gráficos de taxas são injetados automaticamente quando há métricas — "
        "nunca referencie 'gráficos acima' ou 'Gráfico 1/2/3' no DELIVERABLE)"
        if marketing_mode
        else "markdown table or format requested by the goal"
    )

    prompt = f"""{persona}

Goal: {state['goal']}
Client: {state.get('client_id') or 'não definido'}
Iteration: {state.get('iteration', 0)}
Max iterations: 10
{state.get('client_context', '')}
{intake_section}
Work so far:
{context}
{tool_section}

Decide one of:
- DONE: goal is sufficiently addressed (only if intake is complete for marketing tasks)
- CONTINUE: more work needed
- HUMAN: critical ambiguity or missing data requires human input (provide question and options)

When DECISION is DONE, you MUST include a DELIVERABLE section with the complete
user-facing answer in the format requested by the goal (e.g. {deliverable_hint}).
Do not repeat KPI cards or funnel charts in DELIVERABLE — they are added automatically from tool metrics.
Do not use Mermaid diagrams or ASCII/emoji bar charts in DELIVERABLE.
Do not reference "gráficos acima", "Gráfico 1", "Gráfico 2" or similar — visuals are injected automatically.
Do not only describe what was done — include the actual narrative content.

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

    if marketing_mode and force_human and decision == "DONE" and not deliverable:
        decision = "HUMAN"
        question = forced_question
        options = forced_options

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
            "intake_complete": False,
            "messages": [AIMessage(content=f"[Critic] Needs human input: {question}")],
            "activity_events": [
                {
                    "step": "critic",
                    "kind": "preview",
                    "title": "Entrada humana necessária",
                    "summary": question,
                    "preview_type": "text",
                    "preview_data": {"content": question, "options": options or []},
                }
            ],
        }

    if decision == "DONE":
        final_deliverable = deliverable
        if marketing_mode:
            manual_results = list(state.get("marketing_tool_results", []))
            auto_results = auto_detect_marketing_tool_results(collect_marketing_context(state))
            merged_results = merge_tool_results(manual_results, auto_results)
            final_deliverable = merge_deliverable_with_visuals(deliverable, merged_results)

        return {
            "current_step": "critic",
            "needs_human": False,
            "next_route": "end",
            "status": "Completed",
            "result": final_deliverable,
            "intake_complete": True,
            "messages": [AIMessage(content=final_deliverable or f"[Critic] Completed.\n{text}")],
            "activity_events": [
                {
                    "step": "critic",
                    "kind": "step_done",
                    "title": "Tarefa concluída",
                    "summary": None,
                    "preview_type": "markdown",
                    "preview_data": {"content": final_deliverable or text},
                }
            ],
        }

    return {
        "current_step": "critic",
        "needs_human": False,
        "next_route": "planner",
        "status": "Running",
        "iteration": state.get("iteration", 0) + 1,
        "messages": [AIMessage(content=f"[Critic] Continue.\n{text}")],
        "activity_events": [
            {
                "step": "critic",
                "kind": "step_done",
                "title": "Continuando trabalho",
                "summary": None,
                "preview_type": "markdown",
                "preview_data": {"content": text[:3000]},
            }
        ],
    }
