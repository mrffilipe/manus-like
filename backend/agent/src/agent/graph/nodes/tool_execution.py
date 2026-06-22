"""Generic tool execution node."""

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message, Tool


TOOLS = [
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


async def tool_execution_node(state: AgentState, ctx: NodeContext) -> dict:
    context_text = "\n".join(
        msg.content for msg in state.get("messages", [])[-5:] if hasattr(msg, "content")
    )
    prompt = f"""You have collected information for goal: {state['goal']}
Context:
{context_text}

Use tools if needed, otherwise provide a working summary."""

    response = await ctx.llm.chat([Message(role="user", content=prompt)], tools=TOOLS)
    tool_outputs: list[dict] = []

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc.name == "summarize":
                tool_outputs.append({"tool": "summarize", "result": tc.arguments.get("text", "")})
        content = f"Executed tools: {tool_outputs}"
    else:
        content = response.content

    return {
        "current_step": "tool_execution",
        "tool_calls": tool_outputs,
        "next_route": "memory",
        "messages": [AIMessage(content=f"[Tools] {content}")],
    }
