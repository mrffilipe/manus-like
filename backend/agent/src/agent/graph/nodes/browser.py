"""Browser node - Playwright via browser-service."""

from langchain_core.messages import AIMessage

from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message


async def browser_node(state: AgentState, ctx: NodeContext) -> dict:
    url_prompt = f"""Given goal: {state['goal']}
Research summary: {state.get('messages', [])[-1].content if state.get('messages') else ''}

Pick one URL to visit from research results: {state.get('research_results', [])}
Reply with only the URL, or 'none' if no URL is suitable."""

    url_response = await ctx.llm.chat([Message(role="user", content=url_prompt)])
    url = url_response.content.strip()

    browser_results: list[dict] = []
    if url and url.lower() != "none" and url.startswith("http"):
        ctx.browser.session_id = state["execution_id"]
        try:
            nav = await ctx.browser.navigate(url)
            extract = await ctx.browser.extract(format="text")
            browser_results.append({"url": url, "navigate": nav, "extract": extract})
            content = f"Visited {url}. Extracted: {extract.get('content', '')[:2000]}"
        except Exception as exc:
            content = f"Browser error visiting {url}: {exc}"
    else:
        content = "No suitable URL to browse."

    return {
        "current_step": "browser",
        "browser_results": browser_results,
        "next_route": "tools",
        "messages": [AIMessage(content=f"[Browser] {content}")],
    }
