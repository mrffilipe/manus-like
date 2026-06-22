"""Browser service FastAPI app."""

from typing import Literal

from fastapi import FastAPI, Header
from pydantic import BaseModel, Field

from browser_service import playwright_ops

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


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/navigate")
async def navigate(
    body: NavigateRequest,
    x_session_id: str | None = Header(default=None),
) -> dict:
    return await playwright_ops.navigate(x_session_id, body.url)


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
