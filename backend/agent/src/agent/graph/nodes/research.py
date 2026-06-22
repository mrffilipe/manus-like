"""Research node - web search via SearXNG."""

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message


async def research_node(state: AgentState, ctx: NodeContext) -> dict:
    query_prompt = f"""Given this goal: {state['goal']}
And plan: {state.get('plan', '')}
Generate a single concise web search query. Reply with only the query text."""

    query_response = await ctx.llm.chat([Message(role="user", content=query_prompt)])
    query = query_response.content.strip().strip('"')

    results = await ctx.search.search(query, limit=5)
    summary_prompt = f"""Summarize these search results for the goal: {state['goal']}

Results:
{results}

Provide a concise summary."""

    summary_response = await ctx.llm.chat([Message(role="user", content=summary_prompt)])

    return {
        "current_step": "research",
        "research_results": results,
        "next_route": "browser",
        "messages": [AIMessage(content=f"[Research] Query: {query}\n{summary_response.content}")],
    }
