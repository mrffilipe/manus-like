"""Tests for client configuration from models."""

from agent.marketing.client_config import ClientConfig, client_from_model
from agent.persistence.models import MarketingClient


def test_client_from_model_builds_context():
    client = MarketingClient(
        slug="ebox",
        name="eBox Digital",
        product="eBox",
        description="Gestão documental",
        profile={
            "icp": {"roles": ["TI"], "company_profile": "Grande porte"},
            "differentiators": ["ISO 27001"],
            "constraints": ["Sem Calendly"],
        },
    )
    config = client_from_model(client)
    assert isinstance(config, ClientConfig)
    text = config.to_context_text()
    assert "eBox" in text
    assert "ISO 27001" in text
