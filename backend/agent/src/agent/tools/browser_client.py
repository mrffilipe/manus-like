"""HTTP client for browser-service."""

from typing import Any

import httpx

from agent.config import settings


class BrowserClient:
    def __init__(self) -> None:
        self.base_url = settings.browser_service_url.rstrip("/")
        self.session_id: str | None = None

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.session_id:
            headers["X-Session-Id"] = self.session_id
        return headers

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()
            if "session_id" in data:
                self.session_id = data["session_id"]
            return data

    async def navigate(self, url: str) -> dict[str, Any]:
        return await self._post("/navigate", {"url": url})

    async def click(self, selector: str) -> dict[str, Any]:
        return await self._post("/click", {"selector": selector})

    async def fill(self, selector: str, value: str) -> dict[str, Any]:
        return await self._post("/fill", {"selector": selector, "value": value})

    async def extract(self, selector: str | None = None, format: str = "text") -> dict[str, Any]:
        return await self._post("/extract", {"selector": selector, "format": format})

    async def screenshot(self) -> dict[str, Any]:
        return await self._post("/screenshot", {})

    async def scroll_capture(self, steps: int = 4) -> dict[str, Any]:
        return await self._post("/scroll-capture", {"steps": steps})
