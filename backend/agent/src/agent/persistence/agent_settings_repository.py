"""Repository for global agent settings."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent.persistence.models import AgentSetting


class AgentSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_setting(self, key: str) -> AgentSetting | None:
        result = await self.session.execute(select(AgentSetting).where(AgentSetting.key == key))
        return result.scalar_one_or_none()

    async def upsert_setting(self, key: str, value: str) -> AgentSetting:
        existing = await self.get_setting(key)
        if existing is not None:
            existing.value = value
            await self.session.commit()
            return existing

        setting = AgentSetting(key=key, value=value)
        self.session.add(setting)
        await self.session.commit()
        return setting
