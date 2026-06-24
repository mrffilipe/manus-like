# Backend — Agente Manus-like

Serviços Python do agente autônomo: orquestração LangGraph, modo consultor de marketing, ferramentas e configuração de infraestrutura.

## Estrutura

```text
backend/
├── agent/              # API FastAPI + worker Redis + LangGraph
│   └── src/agent/
│       ├── api/routes/     # agent, clients, settings
│       ├── graph/          # builder, nós, runner
│       ├── marketing/      # persona, intake, report_formatter, clientes
│       ├── tools/          # marketing_tools, file_extractor, clientes HTTP
│       └── persistence/    # modelos SQLAlchemy, migrations Alembic
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
| `postgres` | `postgres:16` | — (interno) |
| `redis` | `redis:7` | — (interno) |
| `qdrant` | `qdrant/qdrant` | 6333 |

## Modos do agente

| Modo | Quando | Ferramentas |
|------|--------|-------------|
| `general` | Sem `client_id` | `summarize` |
| `marketing_consultant` | `client_id` ou modo explícito | `analyze_funnel`, `compare_campaign_scenarios`, `parse_campaign_report`, `audit_email_copy`, `audit_landing_page`, `rewrite_sequence`, `generate_prompt_package` |

## Endpoints da API (agent-api)

Documentação interativa: http://localhost:8000/docs

### Raiz

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/health` | Health check; migrations Alembic no startup |

### Agente (`/agent`)

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `POST` | `/agent/attachments` | Upload → extração de texto (sem persistir) |
| `POST` | `/agent/run` | Iniciar execução (JSON) |
| `POST` | `/agent/run/upload` | Iniciar execução com arquivos multipart |
| `GET` | `/agent/conversations` | Listar conversas |
| `GET` | `/agent/conversations/{id}/messages` | Mensagens da conversa |
| `DELETE` | `/agent/conversations/{id}` | Apagar conversa + memória Qdrant |
| `GET` | `/agent/status/{id}` | Status, pergunta pendente, resultado |
| `GET` | `/agent/export/{id}/pdf` | Exportar deliverable em PDF |
| `GET` | `/agent/activity/{id}` | Timeline de atividades |
| `GET` | `/agent/events/{id}` | Stream SSE de eventos |
| `POST` | `/agent/resume/{id}` | Retomar após interrupção |
| `POST` | `/agent/continue/{id}` | Enviar resposta human-in-the-loop |

### Clientes (`/agent/clients`)

CRUD de clientes de marketing, recursos (`file`, `link`, `prompt`, `text`), refresh de links via browser-service e artefatos salvos.

### Settings (`/agent/settings`)

GET/PATCH/reset da persona global `marketing_system_prompt`.

### browser-service

`GET /health`, `POST /navigate`, `/click`, `/fill`, `/extract`, `/screenshot`, `/scroll-capture` — sessão via header `X-Session-Id`.

## LangGraph

Sete nós: `planner` → (`research` | `browser` | `tools` | `memory` | `critic`) com cadeia fixa `research → browser → tool_execution → memory → critic`, mais `human_input` para HITL. Checkpoints no Postgres (`thread_id` = `execution_id`).

## Variáveis de ambiente

Veja [`.env.example`](../.env.example) na raiz. Principais:

- `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`
- `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `QDRANT_COLLECTION`
- `BROWSER_SERVICE_URL`, `SEARCH_SERVICE_URL`
- `CORS_ORIGINS` — origens permitidas do frontend
- `CLIENT_FILES_DIR` — volume de uploads de recursos de clientes

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

- `agent-api` enfileira jobs no Redis (`agent:jobs`); `agent-worker` executa o LangGraph com lock por execução.
- Estado persistido no Postgres (execuções, conversas, mensagens, atividades, clientes marketing).
- Checkpoints LangGraph no Postgres via `langgraph-checkpoint-postgres`.
- Memória de longo prazo no Qdrant com embeddings Gemini.
- Browser e search são ferramentas HTTP stateless — sem lógica de agente.
- Deliverables de marketing recebem blocos visuais de gráficos mesclados automaticamente (`report_formatter`) antes da conclusão.

Consulte [specs.md](../specs.md) para o design completo do sistema.
