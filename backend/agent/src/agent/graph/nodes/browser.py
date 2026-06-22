"""Browser node - Playwright via browser-service."""

import asyncio

from langchain_core.messages import AIMessage

from agent.activity.recorder import ActivityRecorder
from agent.graph.deps import NodeContext
from agent.graph.state import AgentState
from agent.llm.base import Message

STREAM_PAUSE_SECONDS = 0.35


def _webpage_preview(
    *,
    url: str,
    title: str,
    screenshot_base64: str | None,
    action: str,
    frame_index: int,
    frame_total: int,
    excerpt: str | None = None,
) -> dict:
    data: dict = {
        "url": url,
        "title": title,
        "action": action,
        "frame_index": frame_index,
        "frame_total": frame_total,
        "scroll_progress": frame_index / max(frame_total - 1, 1),
        "screenshot_mime": "image/jpeg",
    }
    if screenshot_base64:
        data["screenshot_base64"] = screenshot_base64
    if excerpt:
        data["excerpt"] = excerpt
    return data


async def _emit_browser(
    recorder: ActivityRecorder | None,
    *,
    title: str,
    summary: str | None,
    preview_data: dict,
    kind: str = "preview",
) -> None:
    if recorder is None:
        return
    await recorder.record(
        step="browser",
        kind=kind,
        title=title,
        summary=summary,
        preview_type="webpage",
        preview_data=preview_data,
    )
    await asyncio.sleep(STREAM_PAUSE_SECONDS)


async def browser_node(state: AgentState, ctx: NodeContext) -> dict:
    url_prompt = f"""Given goal: {state['goal']}
Research summary: {state.get('messages', [])[-1].content if state.get('messages') else ''}

Pick one URL to visit from research results: {state.get('research_results', [])}
Reply with only the URL, or 'none' if no URL is suitable."""

    url_response = await ctx.llm.chat([Message(role="user", content=url_prompt)])
    url = url_response.content.strip()

    browser_results: list[dict] = []
    recorder = ctx.activity

    if url and url.lower() != "none" and url.startswith("http"):
        ctx.browser.session_id = state["execution_id"]
        await _emit_browser(
            recorder,
            title="Abrindo página",
            summary=None,
            preview_data=_webpage_preview(
                url=url,
                title="Carregando…",
                screenshot_base64=None,
                action="loading",
                frame_index=0,
                frame_total=1,
            ),
            kind="step_start",
        )
        try:
            nav = await ctx.browser.navigate(url)
            page_url = nav.get("url", url)
            page_title = nav.get("title", "")
            initial_shot = nav.get("screenshot_base64")

            scroll_data = await ctx.browser.scroll_capture(steps=4)
            frames: list[str] = scroll_data.get("frames") or []
            if not frames and initial_shot:
                frames = [initial_shot]
            elif initial_shot and frames and frames[0] != initial_shot:
                frames = [initial_shot, *frames]

            frame_total = max(len(frames), 1)

            await _emit_browser(
                recorder,
                title="Página carregada",
                summary=None,
                preview_data=_webpage_preview(
                    url=page_url,
                    title=page_title,
                    screenshot_base64=frames[0] if frames else initial_shot,
                    action="loaded",
                    frame_index=0,
                    frame_total=frame_total,
                ),
            )

            for index, frame in enumerate(frames[1:], start=1):
                await _emit_browser(
                    recorder,
                    title=f"Rolando página ({index}/{frame_total - 1})",
                    summary=None,
                    preview_data=_webpage_preview(
                        url=page_url,
                        title=page_title,
                        screenshot_base64=frame,
                        action="scroll",
                        frame_index=index,
                        frame_total=frame_total,
                    ),
                )

            extract = await ctx.browser.extract(format="text")
            excerpt = (extract.get("content", "") or "")[:600]
            final_shot = frames[-1] if frames else initial_shot
            preview = {"excerpt": excerpt, "screenshot_base64": final_shot}
            browser_results.append(
                {
                    "url": page_url,
                    "navigate": nav,
                    "extract": extract,
                    "preview": preview,
                    "frames": frames,
                }
            )
            content = f"Visited {page_url}. Extracted: {extract.get('content', '')[:2000]}"

            await _emit_browser(
                recorder,
                title="Conteúdo capturado",
                summary=None,
                preview_data=_webpage_preview(
                    url=page_url,
                    title=page_title,
                    screenshot_base64=final_shot,
                    action="done",
                    frame_index=frame_total - 1,
                    frame_total=frame_total,
                    excerpt=excerpt,
                ),
                kind="step_done",
            )
        except Exception as exc:
            content = f"Browser error visiting {url}: {exc}"
            if recorder:
                await recorder.record(
                    step="browser",
                    kind="error",
                    title="Erro ao navegar",
                    summary=str(exc),
                    preview_type="text",
                    preview_data={"content": str(exc)},
                )
    else:
        content = "No suitable URL to browse."
        if recorder:
            await recorder.record(
                step="browser",
                kind="step_done",
                title="Navegação ignorada",
                summary="Nenhuma URL adequada encontrada",
                preview_type="text",
                preview_data={"content": content},
            )

    return {
        "current_step": "browser",
        "browser_results": browser_results,
        "next_route": "tools",
        "messages": [AIMessage(content=f"[Browser] {content}")],
        "activity_events": [],
    }
