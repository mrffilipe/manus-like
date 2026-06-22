# Backend — Manus-like Agent

Python services for the autonomous agent: LangGraph orchestration, tool services, and infrastructure configuration.

## Structure

```text
backend/
├── agent/              # FastAPI API + Redis worker + LangGraph
├── browser-service/    # Isolated Playwright HTTP service
└── infra/
    └── searxng/        # SearXNG settings
```

## Services (via root docker-compose)

| Container | Build path | Port |
|-----------|------------|------|
| `agent-api` | `./backend/agent` | 8000 |
| `agent-worker` | `./backend/agent` | — |
| `browser-service` | `./backend/browser-service` | 3001 |
| `search-service` | SearXNG image + `infra/searxng/settings.yml` | 8080 |
| `postgres` | `postgres:16` | 5432 |
| `redis` | `redis:7` | 6379 |
| `qdrant` | `qdrant/qdrant` | 6333 |

## API endpoints (agent-api)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/agent/run` | Start execution |
| `GET` | `/agent/status/{id}` | Poll status |
| `POST` | `/agent/resume/{id}` | Resume after restart |
| `POST` | `/agent/continue/{id}` | Submit human input |

Interactive docs: http://localhost:8000/docs

## Environment variables

See root [`.env.example`](../.env.example). Key variables:

- `GEMINI_API_KEY`, `GEMINI_MODEL`
- `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`
- `BROWSER_SERVICE_URL`, `SEARCH_SERVICE_URL`
- `CORS_ORIGINS` — allowed frontend origins (default: `http://localhost:3000,http://localhost:5173`)

## Local development

**Agent API:**

```bash
cd backend/agent
pip install -e ".[dev]"
uvicorn agent.main:app --reload --port 8000
```

**Worker:**

```bash
cd backend/agent
python -m agent.worker
```

**Tests:**

```bash
cd backend/agent
pip install -e ".[dev]"
pip install -e "../browser-service"
pytest tests/ -v
```

**Migrations:**

```bash
cd backend/agent
alembic upgrade head
```

## Architecture notes

- `agent-api` enqueues jobs to Redis; `agent-worker` runs the LangGraph.
- State is persisted in Postgres (executions + LangGraph checkpoints).
- Long-term memory uses Qdrant with Gemini embeddings.
- Browser and search services are stateless HTTP tools — no agent logic inside them.

See [specs.md](../specs.md) for the full system design.
