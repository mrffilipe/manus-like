"""Persist and publish execution activity events."""

import uuid
from typing import Any

from agent.persistence.models import ExecutionActivity
from agent.persistence.repository import ExecutionRepository
from agent.queue.redis_queue import RedisQueue

MAX_SCREENSHOT_BASE64_CHARS = 200_000


class ActivityRecorder:
    def __init__(
        self,
        repo: ExecutionRepository,
        queue: RedisQueue | None,
        execution_id: uuid.UUID,
    ) -> None:
        self.repo = repo
        self.queue = queue
        self.execution_id = execution_id

    def _sanitize_preview_data(self, preview_data: dict[str, Any] | None) -> dict[str, Any] | None:
        if not preview_data:
            return preview_data
        data = dict(preview_data)
        screenshot = data.get("screenshot_base64")
        if isinstance(screenshot, str) and len(screenshot) > MAX_SCREENSHOT_BASE64_CHARS:
            data["screenshot_base64"] = screenshot[:MAX_SCREENSHOT_BASE64_CHARS]
            data["screenshot_truncated"] = True
        return data

    def _to_payload(self, activity: ExecutionActivity) -> dict[str, Any]:
        return {
            "id": str(activity.id),
            "execution_id": str(activity.execution_id),
            "step": activity.step,
            "kind": activity.kind,
            "title": activity.title,
            "summary": activity.summary,
            "preview_type": activity.preview_type,
            "preview_data": activity.preview_data,
            "created_at": activity.created_at.isoformat(),
        }

    async def record(
        self,
        *,
        step: str,
        kind: str,
        title: str,
        summary: str | None = None,
        preview_type: str | None = None,
        preview_data: dict[str, Any] | None = None,
    ) -> ExecutionActivity:
        activity = await self.repo.add_activity(
            self.execution_id,
            step=step,
            kind=kind,
            title=title,
            summary=summary,
            preview_type=preview_type,
            preview_data=self._sanitize_preview_data(preview_data),
        )

        if self.queue is not None:
            await self.queue.publish_event(
                str(self.execution_id),
                {"event": "activity", "activity": self._to_payload(activity)},
            )

        return activity

    async def record_events(self, events: list[dict[str, Any]]) -> None:
        for event in events:
            await self.record(
                step=event["step"],
                kind=event["kind"],
                title=event["title"],
                summary=event.get("summary"),
                preview_type=event.get("preview_type"),
                preview_data=event.get("preview_data"),
            )
