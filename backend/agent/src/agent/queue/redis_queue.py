"""Redis job queue."""

import json
import uuid
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as redis
from redis.exceptions import TimeoutError as RedisTimeoutError

from agent.config import settings

JOBS_QUEUE = "agent:jobs"
LOCK_PREFIX = "agent:lock:"
EVENTS_PREFIX = "agent:events:"
LOCK_TTL_SECONDS = 600


class JobType(str, Enum):
    RUN = "run"
    RESUME = "resume"
    CONTINUE = "continue"


@dataclass
class AgentJob:
    execution_id: str
    job_type: JobType
    human_response: str | None = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "execution_id": self.execution_id,
                "job_type": self.job_type.value,
                "human_response": self.human_response,
            }
        )

    @classmethod
    def from_json(cls, data: str) -> "AgentJob":
        payload = json.loads(data)
        return cls(
            execution_id=payload["execution_id"],
            job_type=JobType(payload["job_type"]),
            human_response=payload.get("human_response"),
        )


class RedisQueue:
    def __init__(self) -> None:
        self.redis: redis.Redis | None = None

    async def connect(self) -> None:
        # socket_timeout=None is required for blocking commands (BRPOP).
        self.redis = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=None,
        )

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()

    async def enqueue(self, job: AgentJob) -> None:
        assert self.redis is not None
        await self.redis.lpush(JOBS_QUEUE, job.to_json())
        await self.publish_event(job.execution_id, {"event": "enqueued", "job_type": job.job_type.value})

    async def dequeue(self, timeout: int = 5) -> AgentJob | None:
        assert self.redis is not None
        try:
            result = await self.redis.brpop(JOBS_QUEUE, timeout=timeout)
        except RedisTimeoutError:
            return None
        if result is None:
            return None
        _, data = result
        return AgentJob.from_json(data)

    async def acquire_lock(self, execution_id: str) -> bool:
        assert self.redis is not None
        lock_key = f"{LOCK_PREFIX}{execution_id}"
        acquired = await self.redis.set(lock_key, str(uuid.uuid4()), nx=True, ex=LOCK_TTL_SECONDS)
        return bool(acquired)

    async def release_lock(self, execution_id: str) -> None:
        assert self.redis is not None
        await self.redis.delete(f"{LOCK_PREFIX}{execution_id}")

    async def publish_event(self, execution_id: str, event: dict) -> None:
        assert self.redis is not None
        await self.redis.publish(f"{EVENTS_PREFIX}{execution_id}", json.dumps(event))
