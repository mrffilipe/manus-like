"""Repository for marketing clients and resources."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent.persistence.models import ClientResource, MarketingClient


class ClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_clients(self, *, active_only: bool = True) -> list[MarketingClient]:
        query = select(MarketingClient).order_by(MarketingClient.name.asc())
        if active_only:
            query = query.where(MarketingClient.is_active.is_(True))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_client(self, client_id: uuid.UUID) -> MarketingClient | None:
        result = await self.session.execute(
            select(MarketingClient)
            .where(MarketingClient.id == client_id)
            .options(selectinload(MarketingClient.resources))
        )
        return result.scalar_one_or_none()

    async def get_client_by_slug(self, slug: str) -> MarketingClient | None:
        result = await self.session.execute(
            select(MarketingClient)
            .where(MarketingClient.slug == slug)
            .options(selectinload(MarketingClient.resources))
        )
        return result.scalar_one_or_none()

    async def create_client(
        self,
        *,
        slug: str,
        name: str,
        product: str,
        description: str = "",
        profile: dict | None = None,
    ) -> MarketingClient:
        client = MarketingClient(
            slug=slug,
            name=name,
            product=product,
            description=description,
            profile=profile,
        )
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def update_client(
        self,
        client_id: uuid.UUID,
        *,
        slug: str | None = None,
        name: str | None = None,
        product: str | None = None,
        description: str | None = None,
        profile: dict | None = None,
        is_active: bool | None = None,
    ) -> MarketingClient | None:
        client = await self.get_client(client_id)
        if client is None:
            return None

        if slug is not None:
            client.slug = slug
        if name is not None:
            client.name = name
        if product is not None:
            client.product = product
        if description is not None:
            client.description = description
        if profile is not None:
            client.profile = profile
        if is_active is not None:
            client.is_active = is_active

        client.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def delete_client(self, client_id: uuid.UUID) -> bool:
        client = await self.get_client(client_id)
        if client is None:
            return False
        await self.session.delete(client)
        await self.session.commit()
        return True

    async def list_resources(self, client_id: uuid.UUID) -> list[ClientResource]:
        result = await self.session.execute(
            select(ClientResource)
            .where(ClientResource.client_id == client_id)
            .order_by(ClientResource.sort_order.asc(), ClientResource.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_resource(self, resource_id: uuid.UUID) -> ClientResource | None:
        result = await self.session.execute(
            select(ClientResource).where(ClientResource.id == resource_id)
        )
        return result.scalar_one_or_none()

    async def create_resource(
        self,
        client_id: uuid.UUID,
        *,
        resource_type: str,
        title: str,
        category: str | None = None,
        content: str | None = None,
        url: str | None = None,
        file_path: str | None = None,
        extracted_text: str | None = None,
        metadata: dict | None = None,
        sort_order: int | None = None,
    ) -> ClientResource:
        if sort_order is None:
            result = await self.session.execute(
                select(func.coalesce(func.max(ClientResource.sort_order), -1)).where(
                    ClientResource.client_id == client_id
                )
            )
            sort_order = int(result.scalar_one()) + 1

        resource = ClientResource(
            client_id=client_id,
            resource_type=resource_type,
            category=category,
            title=title,
            content=content,
            url=url,
            file_path=file_path,
            extracted_text=extracted_text,
            metadata_=metadata,
            sort_order=sort_order,
        )
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def update_resource(
        self,
        resource_id: uuid.UUID,
        **fields: object,
    ) -> ClientResource | None:
        resource = await self.get_resource(resource_id)
        if resource is None:
            return None

        field_map = {
            "category": "category",
            "title": "title",
            "content": "content",
            "url": "url",
            "file_path": "file_path",
            "extracted_text": "extracted_text",
            "scraped_at": "scraped_at",
            "metadata": "metadata_",
            "sort_order": "sort_order",
            "resource_type": "resource_type",
        }
        for key, value in fields.items():
            if value is None or key not in field_map:
                continue
            setattr(resource, field_map[key], value)

        resource.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def delete_resource(self, resource_id: uuid.UUID) -> ClientResource | None:
        resource = await self.get_resource(resource_id)
        if resource is None:
            return None
        await self.session.delete(resource)
        await self.session.commit()
        return resource

    async def count_resources(self, client_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(ClientResource).where(ClientResource.client_id == client_id)
        )
        return int(result.scalar_one())
