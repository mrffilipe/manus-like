"""Generic and marketing tool execution node."""

import json
from typing import Any

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message, Tool
from agent.tools.marketing_tools import (
    MARKETING_TOOLS,
    execute_marketing_tool,
    format_tool_result,
)

GENERAL_TOOLS = [
    Tool(
        name="summarize",
        description="Summarize collected information",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    ),
]


def _marketing_tools_as_llm_tools() -> list[Tool]:
    return [
        Tool(name=item["name"], description=item["description"], parameters=item["parameters"])
        for item in MARKETING_TOOLS
    ]


def _client_raw_context(state: AgentState) -> dict[str, Any]:
    profile_hint: dict[str, Any] = {}
    ctx = state.get("client_context", "")
    if "diferenciais" in ctx.lower() or "differentiators" in ctx.lower():
        profile_hint["differentiators"] = []
    if state.get("client_id"):
        profile_hint["client_id"] = state["client_id"]
    return profile_hint


async def tool_execution_node(state: AgentState, ctx: NodeContext) -> dict:
    context_text = "\n".join(
        msg.content for msg in state.get("messages", [])[-8:] if hasattr(msg, "content")
    )
    attachments_text = "\n".join(
        attachment.get("extracted_text", "") for attachment in state.get("attachments", [])
    )
    marketing_mode = state.get("agent_mode") == "marketing_consultant"
    tools = _marketing_tools_as_llm_tools() if marketing_mode else GENERAL_TOOLS

    prompt = f"""You have collected information for goal: {state['goal']}
Client: {state.get('client_id') or 'não definido'}
Context:
{context_text}

Attachments:
{attachments_text[:6000] or 'None'}

Use the available tools when they help answer the goal. For marketing tasks:
- parse_campaign_report or analyze_funnel when metrics are present
- audit_email_copy when email text is available
- audit_landing_page when LP content is available
- generate_prompt_package when asked to produce prompts for 1:1 generator
"""

    response = await ctx.llm.chat([Message(role="user", content=prompt)], tools=tools)
    tool_outputs: list[dict] = []
    marketing_results: list[dict] = list(state.get("marketing_tool_results", []))
    client_context = _client_raw_context(state)

    if response.tool_calls:
        for tc in response.tool_calls:
            if marketing_mode:
                result = execute_marketing_tool(tc.name, tc.arguments, client_context)
                formatted = format_tool_result(tc.name, result)
                tool_outputs.append({"tool": tc.name, "result": result})
                marketing_results.append({"tool": tc.name, "result": result})
            elif tc.name == "summarize":
                tool_outputs.append({"tool": "summarize", "result": tc.arguments.get("text", "")})
        content = f"Executed tools: {json.dumps(tool_outputs, ensure_ascii=False)[:4000]}"
    else:
        content = response.content

    preview_content = content
    if tool_outputs:
        previews = []
        for item in tool_outputs:
            previews.append(format_tool_result(item["tool"], item["result"]))
        preview_content = "\n\n".join(previews)

    return {
        "current_step": "tool_execution",
        "tool_calls": tool_outputs,
        "marketing_tool_results": marketing_results,
        "next_route": "memory",
        "messages": [AIMessage(content=f"[Tools] {content}")],
        "activity_events": [
            {
                "step": "tool_execution",
                "kind": "step_done",
                "title": "Ferramentas executadas",
                "summary": None,
                "preview_type": "markdown",
                "preview_data": {"content": preview_content[:3000]},
            }
        ],
    }
