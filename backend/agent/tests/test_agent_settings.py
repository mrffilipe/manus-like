"""Tests for agent settings and persona resolution."""

import pytest

from agent.marketing.agent_settings_service import (
    MAX_PROMPT_LENGTH,
    MIN_PROMPT_LENGTH,
    AgentSettingsService,
)
from agent.marketing.persona import DEFAULT_MARKETING_SYSTEM_PROMPT, resolve_marketing_system_prompt


def test_resolve_marketing_system_prompt_uses_state_when_present():
    custom = "x" * 120
    assert resolve_marketing_system_prompt(custom) == custom


def test_resolve_marketing_system_prompt_falls_back_to_default():
    assert resolve_marketing_system_prompt("") == DEFAULT_MARKETING_SYSTEM_PROMPT
    assert resolve_marketing_system_prompt(None) == DEFAULT_MARKETING_SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_update_marketing_system_prompt_validates_length():
    service = AgentSettingsService(session=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=str(MIN_PROMPT_LENGTH)):
        await service.update_marketing_system_prompt("short")

    with pytest.raises(ValueError, match=str(MAX_PROMPT_LENGTH)):
        await service.update_marketing_system_prompt("x" * (MAX_PROMPT_LENGTH + 1))
