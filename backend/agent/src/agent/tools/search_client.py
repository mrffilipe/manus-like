"""HTTP client for SearXNG search-service."""

from typing import Any

import httpx

from agent.config import settings


class SearchClient:
    def __init__(self) -> None:
        self.base_url = settings.search_service_url.rstrip("/")

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={"q": query, "format": "json"},
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError:
                return []

        results = []
        for item in data.get("results", [])[:limit]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                }
            )
        return results
