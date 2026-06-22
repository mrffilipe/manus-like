"""Browser service FastAPI app."""

import logging
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from playwright.async_api import Error as PlaywrightError

from browser_service import playwright_ops

logger = logging.getLogger(__name__)

app = FastAPI(title="Browser Service", version="0.1.0")


class NavigateRequest(BaseModel):
    url: str


class ClickRequest(BaseModel):
    selector: str


class FillRequest(BaseModel):
    selector: str
    value: str


class ExtractRequest(BaseModel):
    selector: str | None = None
    format: Literal["text", "html"] = "text"


class ScrollCaptureRequest(BaseModel):
    steps: int = 4


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/navigate")
async def navigate(
    body: NavigateRequest,
    x_session_id: str | None = Header(default=None),
) -> dict:
    try:
        return await playwright_ops.navigate(x_session_id, body.url)
    except PlaywrightError as exc:
        logger.exception("Navigate failed for %s", body.url)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/click")
async def click(
    body: ClickRequest,
    x_session_id: str | None = Header(default=None),
) -> dict:
    return await playwright_ops.click(x_session_id, body.selector)


@app.post("/fill")
async def fill(
    body: FillRequest,
    x_session_id: str | None = Header(default=None),
) -> dict:
    return await playwright_ops.fill(x_session_id, body.selector, body.value)


@app.post("/extract")
async def extract(
    body: ExtractRequest,
    x_session_id: str | None = Header(default=None),
) -> dict:
    return await playwright_ops.extract(x_session_id, body.selector, body.format)


@app.post("/screenshot")
async def screenshot(x_session_id: str | None = Header(default=None)) -> dict:
    return await playwright_ops.screenshot(x_session_id)


@app.post("/scroll-capture")
async def scroll_capture(
    body: ScrollCaptureRequest,
    x_session_id: str | None = Header(default=None),
) -> dict:
    try:
        return await playwright_ops.scroll_and_capture(x_session_id, body.steps)
    except PlaywrightError as exc:
        logger.exception("Scroll capture failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
