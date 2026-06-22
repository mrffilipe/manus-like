# Manus-like Autonomous Agent System

Monorepo for a containerized autonomous agent with a React admin UI and Python backend services.

## Repository layout

```text
manus-like/
├── frontend/          # React + MUI SPA (Kyvo architecture)
├── backend/
│   ├── agent/         # FastAPI + LangGraph core
│   ├── browser-service/
│   └── infra/
├── docker-compose.yml
├── specs.md
└── .env.example
```

## Quick start

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Set `GEMINI_API_KEY` in `.env`.

3. Start all services:

```bash
docker compose up --build
```

4. Open the UI:

- **Frontend:** http://localhost:3000
- **Agent API:** http://localhost:8000
- **API docs:** http://localhost:8000/docs

## Services

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 3000 | React UI |
| `agent-api` | 8000 | Agent REST API |
| `browser-service` | 3001 | Playwright automation |
| `search-service` | 8080 | SearXNG web search |
| `postgres` | 5432 | Operational state |
| `redis` | 6379 | Job queue |
| `qdrant` | 6333 | Vector memory |

## Documentation

- [Frontend README](frontend/README.md) | [pt-BR](frontend/README.pt-BR.md)
- [Backend README](backend/README.md) | [pt-BR](backend/README.pt-BR.md)
- [System specification](specs.md)

## Development

**Frontend (local):**

```bash
cd frontend
npm install
npm run dev
```

**Backend tests:**

```bash
cd backend/agent
pip install -e ".[dev]"
pip install -e "../browser-service"
pytest tests/
```

See child READMEs for detailed setup and API usage.
