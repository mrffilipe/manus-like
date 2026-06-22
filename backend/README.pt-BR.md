# Backend — Agente Manus-like

Serviços Python do agente autônomo: orquestração LangGraph, ferramentas e configuração de infraestrutura.

## Estrutura

```text
backend/
├── agent/              # API FastAPI + worker Redis + LangGraph
├── browser-service/    # Serviço HTTP Playwright isolado
└── infra/
    └── searxng/        # Configuração SearXNG
```

## Serviços (via docker-compose na raiz)

| Container | Build | Porta |
|-----------|-------|-------|
| `agent-api` | `./backend/agent` | 8000 |
| `agent-worker` | `./backend/agent` | — |
| `browser-service` | `./backend/browser-service` | 3001 |
| `search-service` | Imagem SearXNG + `infra/searxng/settings.yml` | 8080 |
| `postgres` | `postgres:16` | 5432 |
| `redis` | `redis:7` | 6379 |
| `qdrant` | `qdrant/qdrant` | 6333 |

## Endpoints da API (agent-api)

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/agent/run` | Iniciar execução |
| `GET` | `/agent/status/{id}` | Consultar status |
| `POST` | `/agent/resume/{id}` | Retomar após restart |
| `POST` | `/agent/continue/{id}` | Enviar input humano |

Documentação interativa: http://localhost:8000/docs

## Variáveis de ambiente

Veja [`.env.example`](../.env.example) na raiz. Principais:

- `GEMINI_API_KEY`, `GEMINI_MODEL`
- `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`
- `BROWSER_SERVICE_URL`, `SEARCH_SERVICE_URL`
- `CORS_ORIGINS` — origens permitidas do frontend

## Desenvolvimento local

**API do agente:**

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

**Testes:**

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

## Notas de arquitetura

- `agent-api` enfileira jobs no Redis; `agent-worker` executa o LangGraph.
- Estado persistido no Postgres (execuções + checkpoints LangGraph).
- Memória de longo prazo no Qdrant com embeddings Gemini.
- Browser e search são ferramentas HTTP stateless — sem lógica de agente.

Consulte [specs.md](../specs.md) para o design completo.
