"""Memory node - Qdrant long-term memory."""

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message


async def memory_node(state: AgentState, ctx: NodeContext) -> dict:
    assert ctx.memory is not None

    conversation_id = state.get("conversation_id")
    client_id = state.get("client_id")
    recalled = await ctx.memory.search(
        state["goal"],
        execution_id=state["execution_id"] if not conversation_id and not client_id else None,
        conversation_id=conversation_id,
        client_id=client_id,
        limit=5,
    )
    memory_context = [item["content"] for item in recalled if item.get("content")]

    latest = ""
    if state.get("messages"):
        latest = state["messages"][-1].content if hasattr(state["messages"][-1], "content") else ""

    store_prompt = f"""Extract 1-3 key facts worth remembering from this agent work.
Goal: {state['goal']}
Latest output: {latest}
Reply with one fact per line, or 'none' if nothing worth storing."""

    store_response = await ctx.llm.chat([Message(role="user", content=store_prompt)])
    stored: list[str] = []
    for line in store_response.content.splitlines():
        fact = line.strip().lstrip("-").strip()
        if fact and fact.lower() != "none":
            await ctx.memory.store(
                fact,
                execution_id=state["execution_id"],
                conversation_id=conversation_id,
                client_id=client_id,
                memory_type="fact",
            )
            stored.append(fact)

    return {
        "current_step": "memory",
        "memory_context": memory_context + stored,
        "next_route": "critic",
        "messages": [AIMessage(content=f"[Memory] Recalled {len(memory_context)}, stored {len(stored)} facts")],
        "activity_events": [
            {
                "step": "memory",
                "kind": "step_done",
                "title": "Memória atualizada",
                "summary": f"Recuperados {len(memory_context)}, armazenados {len(stored)} fatos",
                "preview_type": "markdown",
                "preview_data": {
                    "content": "\n".join(f"- {fact}" for fact in memory_context + stored)[:2000]
                    or "Nenhum fato relevante",
                },
            }
        ],
    }
