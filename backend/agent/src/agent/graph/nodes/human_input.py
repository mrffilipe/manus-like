"""Human-in-the-loop node with LangGraph interrupt."""

from langgraph.types import interrupt

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState


async def human_input_node(state: AgentState, ctx: NodeContext) -> dict:
    question = state.get("pending_question") or "Please provide additional input."
    options = state.get("pending_options")

    payload = {"question": question, "options": options}
    human_response = interrupt(payload)

    return {
        "current_step": "human_input",
        "human_response": str(human_response),
        "pending_question": None,
        "pending_options": None,
        "needs_human": False,
        "status": "Running",
        "next_route": "planner",
        "activity_events": [
            {
                "step": "human_input",
                "kind": "step_done",
                "title": "Resposta recebida",
                "summary": str(human_response)[:200],
                "preview_type": "text",
                "preview_data": {"content": str(human_response)},
            }
        ],
    }
