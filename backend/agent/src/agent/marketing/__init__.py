"""Marketing B2B consultant domain."""

from agent.marketing.client_config import ClientConfig, client_from_model
from agent.marketing.intake import IntakeChecklist, evaluate_intake
from agent.marketing.persona import DEFAULT_MARKETING_SYSTEM_PROMPT, build_client_context_prompt

__all__ = [
    "ClientConfig",
    "IntakeChecklist",
    "DEFAULT_MARKETING_SYSTEM_PROMPT",
    "build_client_context_prompt",
    "client_from_model",
    "evaluate_intake",
]
