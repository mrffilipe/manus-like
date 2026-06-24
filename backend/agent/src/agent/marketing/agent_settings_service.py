"""Global agent settings (persona, etc.)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from agent.marketing.persona import DEFAULT_MARKETING_SYSTEM_PROMPT
from agent.persistence.agent_settings_repository import AgentSettingsRepository

MARKETING_SYSTEM_PROMPT_KEY = "marketing_system_prompt"
MIN_PROMPT_LENGTH = 100
MAX_PROMPT_LENGTH = 50_000


class AgentSettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AgentSettingsRepository(session)

    async def get_marketing_system_prompt(self) -> str:
        setting = await self.repo.get_setting(MARKETING_SYSTEM_PROMPT_KEY)
        if setting is None or not setting.value.strip():
            return DEFAULT_MARKETING_SYSTEM_PROMPT
        return setting.value

    async def update_marketing_system_prompt(self, text: str) -> str:
        normalized = text.strip()
        if len(normalized) < MIN_PROMPT_LENGTH:
            raise ValueError(f"Prompt must be at least {MIN_PROMPT_LENGTH} characters")
        if len(normalized) > MAX_PROMPT_LENGTH:
            raise ValueError(f"Prompt must be at most {MAX_PROMPT_LENGTH} characters")
        await self.repo.upsert_setting(MARKETING_SYSTEM_PROMPT_KEY, normalized)
        return normalized

    async def reset_marketing_system_prompt(self) -> str:
        await self.repo.upsert_setting(MARKETING_SYSTEM_PROMPT_KEY, DEFAULT_MARKETING_SYSTEM_PROMPT)
        return DEFAULT_MARKETING_SYSTEM_PROMPT
