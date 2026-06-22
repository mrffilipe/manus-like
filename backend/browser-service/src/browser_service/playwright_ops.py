"""Playwright session management and operations."""

import base64
import uuid
from typing import Any

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

_playwright = None
_browser: Browser | None = None
_sessions: dict[str, tuple[BrowserContext, Page]] = {}


async def _ensure_browser() -> Browser:
    global _playwright, _browser
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser


async def get_or_create_session(session_id: str | None) -> tuple[str, Page]:
    sid = session_id or str(uuid.uuid4())
    if sid in _sessions:
        return sid, _sessions[sid][1]

    browser = await _ensure_browser()
    context = await browser.new_context()
    page = await context.new_page()
    _sessions[sid] = (context, page)
    return sid, page


async def navigate(session_id: str | None, url: str) -> dict[str, Any]:
    sid, page = await get_or_create_session(session_id)
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    title = await page.title()
    return {
        "session_id": sid,
        "url": page.url,
        "title": title,
        "status": "ok",
    }


async def click(session_id: str | None, selector: str) -> dict[str, Any]:
    sid, page = await get_or_create_session(session_id)
    await page.click(selector, timeout=10000)
    return {"session_id": sid, "status": "ok", "selector": selector}


async def fill(session_id: str | None, selector: str, value: str) -> dict[str, Any]:
    sid, page = await get_or_create_session(session_id)
    await page.fill(selector, value, timeout=10000)
    return {"session_id": sid, "status": "ok", "selector": selector}


async def extract(
    session_id: str | None,
    selector: str | None = None,
    format: str = "text",
) -> dict[str, Any]:
    sid, page = await get_or_create_session(session_id)
    if selector:
        element = page.locator(selector)
        content = await element.inner_text() if format == "text" else await element.inner_html()
    else:
        content = await page.inner_text("body") if format == "text" else await page.content()
    return {"session_id": sid, "content": content[:10000], "format": format}


async def screenshot(session_id: str | None) -> dict[str, Any]:
    sid, page = await get_or_create_session(session_id)
    data = await page.screenshot(type="png")
    encoded = base64.b64encode(data).decode("ascii")
    return {"session_id": sid, "screenshot_base64": encoded, "format": "png"}
