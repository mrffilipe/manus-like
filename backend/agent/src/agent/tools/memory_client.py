"""Qdrant long-term memory client."""

import uuid
from datetime import datetime, timezone
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchAny, MatchValue, PointStruct, VectorParams

from agent.config import settings
from agent.llm.base import LLMProvider


class MemoryClient:
    def __init__(self, llm: LLMProvider) -> None:
        self.client = AsyncQdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        self.llm = llm
        self._initialized = False

    async def ensure_collection(self, vector_size: int = 768) -> None:
        if self._initialized:
            return
        collections = await self.client.get_collections()
        names = [c.name for c in collections.collections]
        if self.collection not in names:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        self._initialized = True

    async def store(
        self,
        content: str,
        *,
        execution_id: str,
        user_id: str | None = None,
        memory_type: str = "fact",
    ) -> None:
        embeddings = await self.llm.embed([content])
        if not embeddings:
            return
        await self.ensure_collection(len(embeddings[0]))
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[0],
            payload={
                "content": content,
                "execution_id": execution_id,
                "user_id": user_id,
                "type": memory_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        await self.client.upsert(collection_name=self.collection, points=[point])

    async def search(
        self,
        query: str,
        *,
        execution_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        embeddings = await self.llm.embed([query])
        if not embeddings:
            return []
        await self.ensure_collection(len(embeddings[0]))

        query_filter = None
        if execution_id:
            query_filter = Filter(
                should=[FieldCondition(key="execution_id", match=MatchValue(value=execution_id))]
            )

        response = await self.client.query_points(
            collection_name=self.collection,
            query=embeddings[0],
            limit=limit,
            query_filter=query_filter,
        )
        return [
            {
                "content": hit.payload.get("content", "") if hit.payload else "",
                "score": hit.score,
                "type": hit.payload.get("type", "") if hit.payload else "",
            }
            for hit in response.points
        ]

    async def delete_by_execution_ids(self, execution_ids: list[str]) -> None:
        if not execution_ids:
            return

        collections = await self.client.get_collections()
        if self.collection not in [collection.name for collection in collections.collections]:
            return

        await self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[FieldCondition(key="execution_id", match=MatchAny(any=execution_ids))]
            ),
        )
