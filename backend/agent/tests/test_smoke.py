"""Smoke tests for agent system."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from agent.api.routes.agent import get_queue
from agent.graph.state import AgentState
from agent.llm.base import Message
from agent.main import app
from agent.queue.redis_queue import AgentJob, JobType, RedisQueue


class FakeQueue(RedisQueue):
    def __init__(self) -> None:
        self.jobs: list[AgentJob] = []

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def enqueue(self, job: AgentJob) -> None:
        self.jobs.append(job)

    async def dequeue(self, timeout: int = 5) -> AgentJob | None:
        return None


@pytest.fixture
def fake_queue():
    return FakeQueue()


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_agent_state_structure():
    state = AgentState(
        goal="test",
        messages=[],
        current_step="planner",
        tool_calls=[],
        memory_context=[],
        execution_id="123",
        status="Running",
        pending_question=None,
        pending_options=None,
        iteration=0,
        next_route="research",
        plan="",
        research_results=[],
        browser_results=[],
        needs_human=False,
        human_response=None,
        result=None,
        activity_events=[],
    )
    assert state["goal"] == "test"
    assert state["status"] == "Running"


@pytest.mark.asyncio
async def test_gemini_provider_chat_mock():
    from agent.llm.gemini import GeminiProvider

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.candidates = [
        MagicMock(content=MagicMock(parts=[MagicMock(text="Hello", function_call=None)]))
    ]
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("agent.llm.gemini.genai.Client", return_value=mock_client):
        provider = GeminiProvider()
        result = await provider.chat([Message(role="user", content="hi")])
        assert result.content == "Hello"


@pytest.mark.asyncio
async def test_search_client_parses_results():
    from agent.tools.search_client import SearchClient

    client = SearchClient()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "results": [{"title": "T", "url": "http://x.com", "content": "C"}]
    }

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=mock_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    with patch("agent.tools.search_client.httpx.AsyncClient", return_value=mock_http):
        results = await client.search("test query")

    assert len(results) == 1
    assert results[0]["title"] == "T"


@pytest.mark.asyncio
async def test_browser_service_health():
    from browser_service.main import app as browser_app

    transport = ASGITransport(app=browser_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fake_queue_enqueue():
    queue = FakeQueue()
    job = AgentJob(execution_id=str(uuid.uuid4()), job_type=JobType.RUN)
    await queue.enqueue(job)
    assert len(queue.jobs) == 1
    assert queue.jobs[0].job_type == JobType.RUN


@pytest.mark.asyncio
async def test_run_agent_enqueues_job(fake_queue):
    mock_execution = MagicMock()
    mock_execution.id = uuid.uuid4()
    mock_execution.conversation_id = uuid.uuid4()
    mock_repo = AsyncMock()
    mock_repo.create_execution = AsyncMock(return_value=mock_execution)
    mock_session = AsyncMock()

    async def override_queue():
        return fake_queue

    async def override_session():
        yield mock_session

    app.dependency_overrides[get_queue] = override_queue
    from agent.persistence.database import get_session

    app.dependency_overrides[get_session] = override_session

    with patch("agent.api.routes.agent.ExecutionRepository", return_value=mock_repo):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/agent/run", json={"goal": "test goal"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(fake_queue.jobs) == 1


@pytest.mark.asyncio
async def test_continue_requires_waiting_status(fake_queue):
    mock_execution = MagicMock()
    mock_execution.id = uuid.uuid4()
    mock_execution.conversation_id = uuid.uuid4()
    mock_execution.status = "Running"
    mock_repo = AsyncMock()
    mock_repo.get_execution = AsyncMock(return_value=mock_execution)
    mock_session = AsyncMock()

    async def override_queue():
        return fake_queue

    async def override_session():
        yield mock_session

    app.dependency_overrides[get_queue] = override_queue
    from agent.persistence.database import get_session

    app.dependency_overrides[get_session] = override_session

    with patch("agent.api.routes.agent.ExecutionRepository", return_value=mock_repo):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/agent/continue/{mock_execution.id}",
                json={"answer": "Brasil"},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_agent_activity_list():
    mock_execution = MagicMock()
    mock_execution.id = uuid.uuid4()
    mock_execution.conversation_id = uuid.uuid4()
    mock_repo = AsyncMock()
    mock_repo.get_execution = AsyncMock(return_value=mock_execution)
    mock_repo.list_activities = AsyncMock(return_value=[])
    mock_session = AsyncMock()

    async def override_session():
        yield mock_session

    from agent.persistence.database import get_session

    app.dependency_overrides[get_session] = override_session

    with patch("agent.api.routes.agent.ExecutionRepository", return_value=mock_repo):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/agent/activity/{mock_execution.id}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["activities"] == []
