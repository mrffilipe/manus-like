# Backend — Manus-like Agent

Python services for the autonomous agent: LangGraph orchestration, marketing consultant mode, tool services, and infrastructure configuration.

## Structure

```text
backend/
├── agent/              # FastAPI API + Redis worker + LangGraph
│   └── src/agent/
│       ├── api/routes/     # agent, clients, settings
│       ├── graph/          # LangGraph builder, nodes, runner
│       ├── marketing/      # persona, intake, report_formatter, clients
│       ├── tools/          # marketing_tools, file_extractor, HTTP clients
│       └── persistence/    # SQLAlchemy models, Alembic migrations
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
| `postgres` | `postgres:16` | — (internal) |
| `redis` | `redis:7` | — (internal) |
| `qdrant` | `qdrant/qdrant` | 6333 |

## Agent modes

| Mode | When | Tools |
|------|------|-------|
| `general` | No `client_id` | `summarize` |
| `marketing_consultant` | `client_id` or explicit mode | `analyze_funnel`, `compare_campaign_scenarios`, `parse_campaign_report`, `audit_email_copy`, `audit_landing_page`, `rewrite_sequence`, `generate_prompt_package` |

## API endpoints (agent-api)

Interactive docs: http://localhost:8000/docs

### Root

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check; Alembic migrations on startup |

### Agent (`/agent`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/agent/attachments` | Upload → text extraction (no persist) |
| `POST` | `/agent/run` | Start execution (JSON) |
| `POST` | `/agent/run/upload` | Start execution with multipart files |
| `GET` | `/agent/conversations` | List conversations |
| `GET` | `/agent/conversations/{id}/messages` | Conversation messages |
| `DELETE` | `/agent/conversations/{id}` | Delete conversation + Qdrant memory |
| `GET` | `/agent/status/{id}` | Poll status, pending question, result |
| `GET` | `/agent/export/{id}/pdf` | Export deliverable as PDF |
| `GET` | `/agent/activity/{id}` | Activity timeline |
| `GET` | `/agent/events/{id}` | SSE event stream |
| `POST` | `/agent/resume/{id}` | Resume after interruption |
| `POST` | `/agent/continue/{id}` | Submit human-in-the-loop answer |

### Clients (`/agent/clients`)

CRUD for marketing clients, resources (`file`, `link`, `prompt`, `text`), link refresh via browser-service, and saved artifacts.

### Settings (`/agent/settings`)

GET/PATCH/reset the global `marketing_system_prompt` persona.

### browser-service

`GET /health`, `POST /navigate`, `/click`, `/fill`, `/extract`, `/screenshot`, `/scroll-capture` — session via `X-Session-Id` header.

## LangGraph

Seven nodes: `planner` → (`research` | `browser` | `tools` | `memory` | `critic`) with fixed chain `research → browser → tool_execution → memory → critic`, plus `human_input` for HITL. Checkpoints in Postgres (`thread_id` = `execution_id`).

## Environment variables

See root [`.env.example`](../.env.example). Key variables:

- `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`
- `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `QDRANT_COLLECTION`
- `BROWSER_SERVICE_URL`, `SEARCH_SERVICE_URL`
- `CORS_ORIGINS` — allowed frontend origins (default: `http://localhost:3000,http://localhost:5173`)
- `CLIENT_FILES_DIR` — client resource uploads volume

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

- `agent-api` enqueues jobs to Redis (`agent:jobs`); `agent-worker` runs the LangGraph with per-execution locks.
- State persisted in Postgres (executions, conversations, messages, activities, marketing clients).
- LangGraph checkpoints in Postgres via `langgraph-checkpoint-postgres`.
- Long-term memory in Qdrant with Gemini embeddings.
- Browser and search are stateless HTTP tools — no agent logic inside them.
- Marketing deliverables get visual chart blocks merged automatically (`report_formatter`) before completion.

See [specs.md](../specs.md) for the full system design.
