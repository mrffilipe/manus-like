"""Build activity events from graph node updates."""

from typing import Any


def _message_text(update: dict[str, Any]) -> str:
    messages = update.get("messages") or []
    if not messages:
        return ""
    last = messages[-1]
    return last.content if hasattr(last, "content") else str(last)


def build_fallback_activities(node_name: str, update: dict[str, Any]) -> list[dict[str, Any]]:
    text = _message_text(update)
    summary = text[:300] if text else None

    if node_name == "planner":
        plan = update.get("plan", "")
        return [
            {
                "step": "planner",
                "kind": "step_done",
                "title": "Planejamento concluído",
                "summary": plan[:200] if plan else summary,
                "preview_type": "text",
                "preview_data": {"content": plan[:1500] if plan else text[:1500]},
            }
        ]

    if node_name == "research":
        results = update.get("research_results") or []
        return [
            {
                "step": "research",
                "kind": "preview",
                "title": "Resultados da pesquisa",
                "summary": summary,
                "preview_type": "search_results",
                "preview_data": {
                    "results": [
                        {"title": item.get("title", ""), "url": item.get("url", "")}
                        for item in results[:5]
                    ],
                },
            }
        ]

    if node_name == "browser":
        browser_results = update.get("browser_results") or []
        if browser_results:
            item = browser_results[0]
            nav = item.get("navigate") or {}
            extract = item.get("extract") or {}
            preview = item.get("preview") or {}
            return [
                {
                    "step": "browser",
                    "kind": "preview",
                    "title": "Lendo página",
                    "summary": nav.get("title") or item.get("url"),
                    "preview_type": "webpage",
                    "preview_data": {
                        "url": item.get("url", ""),
                        "title": nav.get("title", ""),
                        "excerpt": preview.get("excerpt") or (extract.get("content", "") or "")[:500],
                        "screenshot_base64": preview.get("screenshot_base64"),
                    },
                }
            ]
        return [
            {
                "step": "browser",
                "kind": "step_done",
                "title": "Navegação",
                "summary": summary,
                "preview_type": "text",
                "preview_data": {"content": text[:1000]},
            }
        ]

    if node_name == "tool_execution":
        return [
            {
                "step": "tool_execution",
                "kind": "step_done",
                "title": "Ferramentas executadas",
                "summary": summary,
                "preview_type": "text",
                "preview_data": {"content": text[:1500]},
            }
        ]

    if node_name == "memory":
        return [
            {
                "step": "memory",
                "kind": "step_done",
                "title": "Memória atualizada",
                "summary": summary,
                "preview_type": "text",
                "preview_data": {"content": text[:500]},
            }
        ]

    if node_name == "critic":
        result = update.get("result")
        status = update.get("status", "Running")
        title = "Tarefa concluída" if status == "Completed" else "Avaliando progresso"
        preview_type = "markdown" if result else "text"
        return [
            {
                "step": "critic",
                "kind": "step_done",
                "title": title,
                "summary": summary,
                "preview_type": preview_type,
                "preview_data": {"content": (result or text)[:2000]},
            }
        ]

    if node_name == "human_input":
        return [
            {
                "step": "human_input",
                "kind": "step_done",
                "title": "Resposta recebida",
                "summary": summary,
                "preview_type": "text",
                "preview_data": {"content": text[:500]},
            }
        ]

    return [
        {
            "step": node_name,
            "kind": "step_done",
            "title": node_name.replace("_", " ").title(),
            "summary": summary,
            "preview_type": "text",
            "preview_data": {"content": text[:1000]},
        }
    ]
