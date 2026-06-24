"""Tests for client service context building."""

import uuid

from agent.marketing.client_service import build_context_from_client, resources_to_attachments
from agent.persistence.models import ClientResource, MarketingClient


def test_build_context_includes_resources():
    client_id = uuid.uuid4()
    client = MarketingClient(
        id=client_id,
        slug="test",
        name="Test Co",
        product="Test",
        description="Desc",
        profile={"differentiators": ["A"]},
    )
    resources = [
        ClientResource(
            id=uuid.uuid4(),
            client_id=client_id,
            resource_type="prompt",
            title="Base",
            content="Prompt content here",
            sort_order=0,
        ),
        ClientResource(
            id=uuid.uuid4(),
            client_id=client_id,
            resource_type="link",
            title="Site",
            url="https://example.com",
            extracted_text="Page text",
            sort_order=1,
        ),
    ]
    context = build_context_from_client(client, resources)
    assert "Test Co" in context
    assert "Prompt content here" in context
    assert "Page text" in context

    attachments = resources_to_attachments(resources)
    assert len(attachments) == 2
