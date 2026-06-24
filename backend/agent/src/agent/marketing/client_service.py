"""Marketing client business logic — DB-backed context and resource loading."""

from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent.config import settings
from agent.marketing.client_config import ClientConfig, client_from_model
from agent.persistence.client_repository import ClientRepository
from agent.persistence.models import ClientResource, MarketingClient
from agent.tools.browser_client import BrowserClient
from agent.tools.file_extractor import extract_text_from_bytes


def _client_files_root() -> Path:
    root = Path(settings.client_files_dir)
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "cliente"


def _resource_text(resource: ClientResource) -> str | None:
    if resource.extracted_text:
        return resource.extracted_text
    if resource.content:
        return resource.content
    return None


def build_context_from_client(client: MarketingClient, resources: list[ClientResource]) -> str:
    config = client_from_model(client)
    lines = [config.to_context_text(), "", "## Recursos cadastrados"]

    for resource in resources:
        header = f"### {resource.title}"
        if resource.category:
            header += f" ({resource.category})"
        lines.append(header)

        if resource.resource_type == "link" and resource.url:
            lines.append(f"URL: {resource.url}")

        text = _resource_text(resource)
        if text:
            preview = text[:8000] + ("…" if len(text) > 8000 else "")
            lines.append(preview)
        elif resource.resource_type == "link":
            lines.append("(Conteúdo do link ainda não scrapeado)")

        lines.append("")

    return "\n".join(lines).strip()


def resources_to_attachments(resources: list[ClientResource]) -> list[dict[str, Any]]:
    attachments: list[dict[str, Any]] = []
    for resource in resources:
        text = _resource_text(resource)
        if not text:
            continue
        filename = resource.title
        if resource.resource_type == "link" and resource.url:
            filename = f"{resource.title} ({resource.url})"
        elif resource.file_path:
            filename = Path(resource.file_path).name
        attachments.append(
            {
                "filename": filename,
                "extracted_text": text,
                "content_type": resource.resource_type,
                "resource_id": str(resource.id),
            }
        )
    return attachments


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ClientRepository(session)
        self.browser = BrowserClient()

    async def list_clients(self, *, active_only: bool = True) -> list[MarketingClient]:
        return await self.repo.list_clients(active_only=active_only)

    async def get_client(self, client_id: uuid.UUID) -> MarketingClient | None:
        return await self.repo.get_client(client_id)

    async def resolve_client_id(self, client_ref: str) -> uuid.UUID | None:
        try:
            return uuid.UUID(client_ref)
        except ValueError:
            client = await self.repo.get_client_by_slug(client_ref)
            return client.id if client else None

    async def create_client(
        self,
        *,
        name: str,
        product: str,
        description: str = "",
        slug: str | None = None,
        profile: dict | None = None,
    ) -> MarketingClient:
        return await self.repo.create_client(
            slug=slug or _slugify(name),
            name=name,
            product=product,
            description=description,
            profile=profile,
        )

    async def update_client(self, client_id: uuid.UUID, **fields: Any) -> MarketingClient | None:
        return await self.repo.update_client(client_id, **fields)

    async def delete_client(self, client_id: uuid.UUID) -> bool:
        client = await self.repo.get_client(client_id)
        if client is None:
            return False
        root = _client_files_root() / str(client_id)
        if root.exists():
            for path in sorted(root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            root.rmdir()
        return await self.repo.delete_client(client_id)

    async def create_resource_json(
        self,
        client_id: uuid.UUID,
        *,
        resource_type: str,
        title: str,
        category: str | None = None,
        content: str | None = None,
        url: str | None = None,
        metadata: dict | None = None,
    ) -> ClientResource | None:
        client = await self.repo.get_client(client_id)
        if client is None:
            return None
        return await self.repo.create_resource(
            client_id,
            resource_type=resource_type,
            title=title,
            category=category,
            content=content,
            url=url,
            metadata=metadata,
        )

    async def create_resource_file(
        self,
        client_id: uuid.UUID,
        *,
        title: str,
        filename: str,
        content: bytes,
        category: str | None = None,
    ) -> ClientResource | None:
        client = await self.repo.get_client(client_id)
        if client is None:
            return None

        resource = await self.repo.create_resource(
            client_id,
            resource_type="file",
            title=title,
            category=category,
        )

        dest_dir = _client_files_root() / str(client_id) / str(resource.id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename
        dest_path.write_bytes(content)

        extracted = extract_text_from_bytes(filename, content)
        return await self.repo.update_resource(
            resource.id,
            file_path=str(dest_path),
            extracted_text=extracted.get("extracted_text"),
        )

    async def update_resource(self, resource_id: uuid.UUID, **fields: Any) -> ClientResource | None:
        return await self.repo.update_resource(resource_id, **fields)

    async def delete_resource(self, resource_id: uuid.UUID) -> bool:
        resource = await self.repo.delete_resource(resource_id)
        if resource is None:
            return False
        if resource.file_path:
            path = Path(resource.file_path)
            if path.exists():
                path.unlink()
        return True

    async def scrape_link_resource(self, resource: ClientResource) -> ClientResource | None:
        if resource.resource_type != "link" or not resource.url:
            return resource

        try:
            await self.browser.navigate(resource.url)
            result = await self.browser.extract(format="text")
            text = result.get("content") or result.get("text") or ""
            if not text and isinstance(result.get("data"), str):
                text = result["data"]
            return await self.repo.update_resource(
                resource.id,
                extracted_text=text[:50000] if text else resource.extracted_text,
                scraped_at=datetime.now(timezone.utc),
            )
        except Exception:
            return resource

    async def scrape_all_links(self, client_id: uuid.UUID) -> list[ClientResource]:
        resources = await self.repo.list_resources(client_id)
        links = [r for r in resources if r.resource_type == "link" and r.url]

        async def scrape_one(link: ClientResource) -> ClientResource:
            return await self.scrape_link_resource(link) or link

        if not links:
            return []
        results = await asyncio.gather(*[scrape_one(link) for link in links], return_exceptions=True)
        scraped: list[ClientResource] = []
        for item in results:
            if isinstance(item, ClientResource):
                scraped.append(item)
        return scraped

    async def prepare_execution_context(
        self,
        client_id: uuid.UUID,
        *,
        scrape_links: bool = True,
    ) -> tuple[str, list[dict[str, Any]], int]:
        client = await self.repo.get_client(client_id)
        if client is None:
            return "", [], 0

        if scrape_links:
            await self.scrape_all_links(client_id)
            client = await self.repo.get_client(client_id)
            assert client is not None

        resources = list(client.resources)
        context = build_context_from_client(client, resources)
        attachments = resources_to_attachments(resources)
        link_count = sum(1 for r in resources if r.resource_type == "link")
        return context, attachments, link_count

    async def build_client_config(self, client_id: uuid.UUID) -> ClientConfig | None:
        client = await self.repo.get_client(client_id)
        if client is None:
            return None
        return client_from_model(client)


async def get_client_config_from_db(session: AsyncSession, client_ref: str | None) -> ClientConfig | None:
    if not client_ref:
        return None
    service = ClientService(session)
    resolved = await service.resolve_client_id(client_ref)
    if resolved is None:
        return None
    return await service.build_client_config(resolved)
