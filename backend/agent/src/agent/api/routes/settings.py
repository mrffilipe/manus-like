"""Agent settings API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from agent.api.schemas import AgentSettingsResponse, UpdateAgentSettingsRequest
from agent.marketing.agent_settings_service import AgentSettingsService
from agent.persistence.database import get_session

router = APIRouter(prefix="/agent/settings", tags=["settings"])


async def _get_service(session: AsyncSession = Depends(get_session)) -> AgentSettingsService:
    return AgentSettingsService(session)


@router.get("", response_model=AgentSettingsResponse)
async def get_settings(
    service: AgentSettingsService = Depends(_get_service),
) -> AgentSettingsResponse:
    prompt = await service.get_marketing_system_prompt()
    return AgentSettingsResponse(marketing_system_prompt=prompt)


@router.patch("", response_model=AgentSettingsResponse)
async def update_settings(
    body: UpdateAgentSettingsRequest,
    service: AgentSettingsService = Depends(_get_service),
) -> AgentSettingsResponse:
    try:
        prompt = await service.update_marketing_system_prompt(body.marketing_system_prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AgentSettingsResponse(marketing_system_prompt=prompt)


@router.post("/reset", response_model=AgentSettingsResponse)
async def reset_settings(
    service: AgentSettingsService = Depends(_get_service),
) -> AgentSettingsResponse:
    prompt = await service.reset_marketing_system_prompt()
    return AgentSettingsResponse(marketing_system_prompt=prompt)
