# Especificação do Sistema — Manus-like

Documento de engenharia reversa do estado **atual** do repositório. Descreve o que o sistema implementa hoje, não um roadmap futuro.

---

## Objetivo

Sistema de agente autônomo containerizado com:

- **Backend:** Python 3.11+, FastAPI, LangGraph, Google Gemini
- **Frontend:** React 19 + MUI 9 (arquitetura Kyvo)
- **Infraestrutura:** Docker Compose com serviços desacoplados

### Capacidades implementadas

| Área | O que faz |
|------|-----------|
| Agente geral | Pesquisa web (SearXNG), navegação (Playwright), memória vetorial (Qdrant), resumo de conteúdo |
| Consultor de marketing | Modo vertical B2B: clientes, recursos, intake estruturado, 7 ferramentas de domínio, relatórios com gráficos |
| Conversas | Threads persistentes em Postgres, histórico de mensagens, herança de `client_id` |
| Human-in-the-loop | Pausa com pergunta/opções; retomada via API |
| Observabilidade | Timeline de atividades (REST + SSE), export PDF |
| Continuidade | Checkpoints LangGraph em Postgres; fila Redis com worker separado |

---

## Visão geral da arquitetura

```text
┌─────────────┐     REST / SSE      ┌──────────────┐
│  frontend   │ ◄─────────────────► │  agent-api   │
│  :3000      │                     │  :8000       │
└─────────────┘                     └──────┬───────┘
                                           │ enqueue
                                           ▼
                                    ┌──────────────┐
                                    │    redis     │
                                    │  agent:jobs  │
                                    └──────┬───────┘
                                           │ BRPOP
                                           ▼
                                    ┌──────────────┐
                                    │ agent-worker │
                                    │  LangGraph   │
                                    └──────┬───────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              ▼                            ▼                            ▼
       ┌────────────┐              ┌──────────────┐              ┌────────────┐
       │  postgres  │              │   qdrant     │              │  browser   │
       │  estado +  │              │  memória     │              │  :3001     │
       │ checkpoints│              │  :6333       │              └────────────┘
       └────────────┘              └──────────────┘
                                           │
                                    ┌──────────────┐
                                    │ search-svc   │
                                    │ SearXNG:8080 │
                                    └──────────────┘
```

### Princípios de design (implementados)

1. **agent-api** é a única interface HTTP do agente; não executa o grafo inline.
2. **agent-worker** consome a fila Redis e roda o LangGraph com lock por `execution_id`.
3. **browser-service** e **search-service** são ferramentas HTTP stateless — sem lógica de agente.
4. **Estado persistido** em Postgres (execuções, mensagens, checkpoints LangGraph).
5. **LLM:** Google Gemini para chat e embeddings (abstração em `llm/base.py`, implementação única hoje).

---

## Containers e serviços

Orquestração: `docker-compose.yml` na raiz.

| Serviço | Imagem / build | Porta host | Função |
|---------|----------------|------------|--------|
| `frontend` | `./frontend` | **3000** → 80 (nginx) | SPA React |
| `agent-api` | `./backend/agent` | **8000** | API FastAPI, enfileira jobs, SSE |
| `agent-worker` | `./backend/agent` | — (interno) | Worker Redis, executa LangGraph |
| `browser-service` | `./backend/browser-service` | **3001** | Playwright isolado |
| `search-service` | `searxng/searxng` | **8080** | Busca web JSON |
| `postgres` | `postgres:16` | — (interno) | Dados relacionais + checkpoints |
| `redis` | `redis:7` | — (interno) | Fila, locks, pub/sub de eventos |
| `qdrant` | `qdrant/qdrant` | **6333** | Memória vetorial |

### Volumes Docker

| Volume | Uso |
|--------|-----|
| `postgres_data` | Dados Postgres |
| `qdrant_data` | Vetores Qdrant |
| `client_files` | Uploads de recursos de clientes (`/app/data/client-files`) |

### Healthchecks

Todos os serviços críticos têm healthcheck no Compose. `agent-worker` depende de `agent-api` healthy (migrations Alembic rodam no startup da API).

---

## Fluxo de execução

### 1. Início de tarefa

```text
Cliente (UI ou API)
  → POST /agent/run (ou /agent/run/upload)
  → ExecutionRepository cria AgentExecution + Conversation/Message
  → RedisQueue.enqueue(AgentJob)
  → Resposta: { execution_id, conversation_id, status: "Running" }
```

### 2. Processamento (worker)

```text
agent-worker (BRPOP agent:jobs)
  → Lock Redis agent:lock:{execution_id} (TTL 600s)
  → Carrega checkpoint LangGraph (thread_id = execution_id)
  → Executa grafo até interrupt, conclusão ou falha
  → Publica eventos em agent:events:{execution_id}
  → Atualiza status no Postgres
```

### 3. Acompanhamento (UI)

```text
useChat          → polling GET /agent/status/{id} a cada 2s
useExecutionActivity → SSE GET /agent/events/{id} + poll fallback 3s
                   → GET /agent/activity/{id}
```

### 4. Human-in-the-loop

```text
critic_node → status WaitingHumanInput + pending_question/options
  → interrupt LangGraph (human_input_node)
  → UI exibe pergunta
  → POST /agent/continue/{id} { answer }
  → worker retoma no mesmo checkpoint
```

### 5. Conclusão (modo marketing com client_id)

```text
critic_node → DONE
  → merge de blocos visuais no deliverable (report_formatter)
  → ClientArtifact tipo "deliverable" persistido
  → Mensagem assistant salva na conversa
```

---

## LangGraph

**Arquivos:** `backend/agent/src/agent/graph/`

| Arquivo | Papel |
|---------|-------|
| `builder.py` | Monta o grafo e arestas |
| `runner.py` | Inicializa contexto, executa grafo, finaliza execução |
| `state.py` | `AgentState` (TypedDict) |
| `deps.py` | `NodeContext` — LLM, search, browser, memory, activity |
| `conversation_context.py` | Histórico de conversa para o planner |

### Estado (`AgentState`)

```python
goal: str
messages: list[BaseMessage]          # acumulador LangGraph
current_step: str
tool_calls: list[dict]
memory_context: list[str]
execution_id: str
conversation_id: str | None
status: Running | WaitingHumanInput | Completed | Failed
pending_question: str | None
pending_options: list[str] | None
iteration: int
next_route: str
plan: str
research_results: list[dict]
browser_results: list[dict]
needs_human: bool
human_response: str | None
result: str | None
activity_events: list[dict]            # acumulador
agent_mode: general | marketing_consultant
client_id: str | None
client_context: str
attachments: list[dict]
intake_complete: bool
marketing_tool_results: list[dict]
marketing_system_prompt: str
```

### Nós (7)

| Nó | Arquivo | Responsabilidade |
|----|---------|------------------|
| `planner` | `nodes/planner.py` | LLM planeja próxima rota; em marketing injeta persona + contexto do cliente |
| `research` | `nodes/research.py` | Gera query ou `SKIP_RESEARCH`; chama SearXNG; resume com LLM |
| `browser` | `nodes/browser.py` | Navega URL, scroll-capture, extrai texto; previews `webpage` |
| `tool_execution` | `nodes/tool_execution.py` | Tool-calling LLM (marketing tools ou `summarize`) |
| `memory` | `nodes/memory.py` | Busca Qdrant; extrai e armazena 1–3 fatos |
| `critic` | `nodes/critic.py` | DONE / CONTINUE / HUMAN; intake marketing; merge visual no deliverable |
| `human_input` | `nodes/human_input.py` | `interrupt()` — aguarda resposta humana |

### Grafo e roteamento

```text
                    ┌──────────┐
                    │ planner  │◄────────────────────────────┐
                    └────┬─────┘                             │
         research/browser/tools/memory/critic                  │
              │                                                │
    ┌─────────┼─────────┬──────────────┐                      │
    ▼         │         │              ▼                      │
 research ────┘         │           critic ──► END            │
    │                   │              │                      │
    ▼                   │         human │ planner             │
 browser ───────────────┘              ▼                      │
    │                            human_input ─────────────────┘
    ▼
tool_execution
    │
    ▼
  memory
    │
    ▼
  critic
```

**Entrada:** sempre `planner`.

**Roteamento condicional:**
- `planner` → `next_route`: `research` | `browser` | `tools` | `memory` | `critic`
- `critic` → `next_route`: `planner` | `human` | `end`

**Arestas fixas:** `research → browser → tool_execution → memory → critic` (o `next_route` de `research` não encurta esse caminho).

**Checkpoints:** `langgraph-checkpoint-postgres` (`persistence/checkpoint.py`), `thread_id` = `execution_id`.

**Limite de iterações:** critic força `DONE` quando `iteration >= 10`.

---

## Modos do agente

| Modo | Valor | Quando |
|------|-------|--------|
| Geral | `general` | Sem `client_id` e sem `agent_mode` explícito |
| Consultor de marketing | `marketing_consultant` | `agent_mode` explícito ou `client_id` presente |

### Modo `general`

- Ferramenta exposta ao LLM: `summarize` (resume texto coletado).
- Fluxo completo: pesquisa → browser → tools → memória → crítico.

### Modo `marketing_consultant`

Produto vertical B2B implementado em `backend/agent/src/agent/marketing/` e `tools/marketing_tools.py`.

**Fluxo na execução (`runner.py`):**
1. Carrega `marketing_system_prompt` de `agent_settings` (ou default em `persona.py`).
2. Se `client_id`: resolve slug/UUID, scrape de links, monta `client_context` + anexos de recursos.
3. Planner/critic/tool_execution operam em modo marketing.
4. `metrics_auto_detector` pode invocar ferramentas antes do LLM (regex em mensagens/anexos).
5. Ao completar com `client_id`: persiste `ClientArtifact` tipo `deliverable`.

**Intake proativo (`marketing/intake.py`):** checklist (cliente, estágio, métricas, copies, LP, prompts). `evaluate_intake()` usado pelo critic para decidir se pede mais informações (HITL).

---

## Ferramentas

### Dependências injetadas (`NodeContext`)

| Cliente | Serviço | Uso |
|---------|---------|-----|
| `LLMProvider` | Gemini API | Todos os nós |
| `SearchClient` | SearXNG `:8080` | `research_node` |
| `BrowserClient` | browser-service `:3001` | `browser_node`, scrape de links |
| `MemoryClient` | Qdrant + Gemini embeddings | `memory_node` |
| `ActivityRecorder` | Postgres | Timeline durante execução |

### Ferramentas de marketing (`tools/marketing_tools.py`)

| Ferramenta | Função |
|------------|--------|
| `analyze_funnel` | Taxas de funil, gargalo, recomendações, `chart_stages` |
| `compare_campaign_scenarios` | Baseline vs projetada + blocos visuais |
| `parse_campaign_report` | Regex em texto colado → métricas + análise |
| `audit_email_copy` | Auditoria rule-based de copy B2B (score 1–10) |
| `audit_landing_page` | Auditoria de landing page |
| `rewrite_sequence` | Templates fixos (email 1/2, WhatsApp) |
| `generate_prompt_package` | `knowledge_base` + `instruction` para gerador 1:1 |

### Utilitários (não expostos como tools LLM)

| Módulo | Função |
|--------|--------|
| `file_extractor.py` | PDF, DOCX, XLSX, CSV, texto — usado em uploads |
| `report_formatter.py` | Blocos ` ```chart ` / ` ```kpi `, merge no deliverable |
| `metrics_auto_detector.py` | Detecção automática de métricas em texto |

### browser-service

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/navigate` | Abre URL; retorna título, screenshot base64 |
| POST | `/click` | Clica seletor CSS |
| POST | `/fill` | Preenche campo |
| POST | `/extract` | Extrai texto/HTML |
| POST | `/screenshot` | Screenshot da página |
| POST | `/scroll-capture` | Scroll em N passos + frames JPEG |

Sessão via header `X-Session-Id` (agent usa `execution_id`).

### search-service (SearXNG)

Consumido via `GET {SEARCH_SERVICE_URL}/search?q=...&format=json`. Config: `backend/infra/searxng/settings.yml`.

---

## Human-in-the-loop

### Quando pausa

- Falta informação crítica (intake marketing incompleto)
- Ambiguidade de ação
- Critic retorna rota `human`
- Site/decisão que exige input humano

### Comportamento

1. `status` → `WaitingHumanInput`
2. `pending_question` + `pending_options` (opcional) salvos em `agent_executions` e `human_inputs`
3. Grafo interrompido em `human_input_node`
4. Cliente envia `POST /agent/continue/{execution_id}` com `{ "answer": "..." }`
5. Worker retoma; `human_input_node` injeta resposta e volta ao `planner`

### Resume após falha/restart

`POST /agent/resume/{execution_id}` reenfileira o job sem nova resposta humana.

---

## Memória

### Curto prazo (Postgres)

- Histórico de conversas (`conversations`, `messages`)
- Estado de execução (`agent_executions`)
- Saídas de tools e deliverable (`result`)
- Atividades (`execution_activities`)

### Longo prazo (Qdrant)

- Collection: `agent_memory` (configurável via `QDRANT_COLLECTION`)
- Embeddings: Gemini (`gemini-embedding-001`)
- `memory_node`: busca contexto relevante; extrai e armazena fatos
- Ao deletar conversa: memória Qdrant das execuções associadas é removida

---

## Módulo Marketing (backend)

| Módulo | Caminho | Responsabilidade |
|--------|---------|------------------|
| Persona | `marketing/persona.py` | Prompt padrão, `resolve_marketing_system_prompt`, `build_client_context_prompt` |
| Intake | `marketing/intake.py` | Checklist e `evaluate_intake()` |
| Report formatter | `marketing/report_formatter.py` | Blocos visuais markdown; `merge_deliverable_with_visuals()` |
| Metrics auto-detector | `marketing/metrics_auto_detector.py` | Detecção regex; merge manual/auto de tool results |
| Client config | `marketing/client_config.py` | `ClientConfig` dataclass a partir do `profile` JSONB |
| Client service | `marketing/client_service.py` | CRUD de contexto, scrape, `prepare_execution_context()` |
| Agent settings | `marketing/agent_settings_service.py` | GET/PATCH/reset da persona no DB |

### Clientes e recursos

**Tabela `marketing_clients`:** `slug`, `name`, `product`, `description`, `profile` (JSONB).

**Tipos de recurso (`client_resources`):**

| Tipo | Descrição |
|------|-----------|
| `file` | Upload com extração de texto |
| `link` | URL scrapeável via browser-service (`refresh`) |
| `prompt` | Texto de prompt/instrução |
| `text` | Texto livre |

**Artefatos (`client_artifacts`):** entregáveis persistidos ao completar execução com `client_id` (tipo `deliverable`).

### Blocos visuais no relatório

Gerados por `report_formatter.py` e injetados no deliverable final pelo `critic_node` (não pelo LLM diretamente).

Formato em markdown:

````markdown
```chart
{ "type": "funnel", "title": "...", "stages": [...] }
```
````

Tipos suportados:

| `type` | Uso |
|--------|-----|
| `funnel` | Funil único com estágios, %, absolutos, `highlight` |
| `kpi` | Faixa de KPIs (via fence `kpi` ou `type: kpi`) |
| `funnel_compare` | Dois funis lado a lado (baseline vs projetada) |
| `bar_compare` | Barras agrupadas por métrica |
| `projection` | Cenários com faixas opcionais |

---

## API REST (agent-api)

Base: `http://localhost:8000` — docs: `/docs`

### Raiz

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/health` | `{ "status": "ok" }`; migrations no startup |

### Agente (`/agent`)

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/agent/attachments` | Upload → extração de texto (sem persistir) |
| POST | `/agent/run` | Inicia execução (JSON) |
| POST | `/agent/run/upload` | Inicia execução multipart + arquivos |
| GET | `/agent/conversations` | Lista conversas (`user_id`, `limit`) |
| GET | `/agent/conversations/{id}/messages` | Mensagens da conversa |
| DELETE | `/agent/conversations/{id}` | Apaga conversa + memória Qdrant |
| GET | `/agent/status/{execution_id}` | Status, pergunta pendente, resultado |
| GET | `/agent/export/{execution_id}/pdf` | Exporta deliverable em PDF |
| GET | `/agent/activity/{execution_id}` | Timeline (`since` = UUID opcional) |
| GET | `/agent/events/{execution_id}` | **SSE** — stream Redis até estado terminal |
| POST | `/agent/resume/{execution_id}` | Retoma execução interrompida/falha |
| POST | `/agent/continue/{execution_id}` | Responde human-in-the-loop |

**Body `RunAgentRequest` (campos principais):** `goal`, `user_id`, `conversation_id`, `client_id`, `agent_mode`, `attachments`.

### Clientes (`/agent/clients`)

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/agent/clients` | Lista clientes |
| POST | `/agent/clients` | Cria cliente |
| GET | `/agent/clients/{client_id}` | Detalhe (UUID ou slug) |
| PATCH | `/agent/clients/{client_id}` | Atualiza |
| DELETE | `/agent/clients/{client_id}` | Remove + arquivos |
| POST | `/agent/clients/{id}/resources` | Cria recurso JSON |
| POST | `/agent/clients/{id}/resources/upload` | Upload arquivo |
| PATCH | `/agent/clients/{id}/resources/{resource_id}` | Atualiza recurso |
| DELETE | `/agent/clients/{id}/resources/{resource_id}` | Remove |
| POST | `/agent/clients/{id}/resources/{resource_id}/refresh` | Re-scrape de link |
| GET | `/agent/clients/{id}/artifacts` | Artefatos (`artifact_type` opcional) |

### Settings (`/agent/settings`)

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/agent/settings` | Retorna `marketing_system_prompt` |
| PATCH | `/agent/settings` | Atualiza persona (100–50.000 chars) |
| POST | `/agent/settings/reset` | Restaura persona padrão |

### Redis (interno)

| Chave / canal | Uso |
|---------------|-----|
| `agent:jobs` | Fila de jobs (BRPOP) |
| `agent:lock:{execution_id}` | Lock distribuído (TTL 600s) |
| `agent:events:{execution_id}` | Pub/sub para SSE |

---

## Banco de dados

**ORM:** SQLAlchemy async (`asyncpg`). **Migrations:** Alembic (`backend/agent/alembic/`).

| Revisão | Conteúdo |
|---------|----------|
| `001_initial_schema` | Schema completo inicial |
| `002_agent_settings` | Tabela `agent_settings` + seed persona marketing |

### Tabelas da aplicação

| Tabela | Propósito |
|--------|-----------|
| `conversations` | Threads (`user_id`, `client_id`, `title`) |
| `agent_executions` | Execuções (`goal`, `agent_mode`, `client_id`, `attachments`, `status`, `result`, HITL) |
| `messages` | Mensagens user/assistant |
| `human_inputs` | Perguntas e respostas HITL |
| `execution_activities` | Timeline (step, kind, preview_type, preview_data) |
| `marketing_clients` | Clientes B2B |
| `client_resources` | Recursos por cliente |
| `client_artifacts` | Entregáveis persistidos |
| `agent_settings` | KV (`marketing_system_prompt`) |

**Status de execução:** `Running`, `WaitingHumanInput`, `Completed`, `Failed`.

**Checkpoints LangGraph:** tabelas gerenciadas por `AsyncPostgresSaver.setup()` (separadas do schema Alembic da aplicação).

---

## Integração LLM

**Provedor:** Google Gemini (`llm/gemini.py`).

| Aspecto | Valor padrão |
|---------|--------------|
| Chat | `gemini-2.0-flash` (`GEMINI_MODEL`) |
| Embeddings | `gemini-embedding-001` (`GEMINI_EMBEDDING_MODEL`) |
| SDK | `google-genai` |
| Tool calling | `FunctionDeclaration` nativo Gemini |
| Abstração | `llm/base.py` — `LLMProvider`, `Message`, `Tool`, `LLMResponse` |

**Requisito:** `GEMINI_API_KEY` obrigatória em produção.

> OpenAI e Claude estão previstos na abstração conceitual, mas **não há implementação** além do Gemini hoje.

---

## Exportação

| Recurso | Implementação |
|---------|---------------|
| PDF | `GET /agent/export/{execution_id}/pdf` → `export/pdf_export.py` |
| Motor | `xhtml2pdf` (HTML a partir de markdown simplificado) |
| Conteúdo | `execution.result` ou última mensagem assistant |
| Limitação | Blocos `chart` viram `<pre>` — gráficos interativos não renderizam no PDF |

Não há export JSON/CSV/HTML dedicado.

---

## Frontend

**Stack:** React 19, TypeScript 6, Vite 8, MUI 9, `@mui/x-charts`, React Router 7, Axios, `react-markdown` + `remark-gfm`.

**Entry:** `frontend/src/main.tsx` — tema claro/escuro, locale pt-BR.

### Rotas ativas

| Rota | Página | Função |
|------|--------|--------|
| `/` | `ChatPage` | Nova conversa + seletor de cliente |
| `/c/:conversationId` | `ChatPage` | Conversa existente |
| `/clients` | `ClientsPage` | Lista e criação de clientes |
| `/clients/:clientId` | `ClientDetailPage` | Perfil + CRUD de recursos |
| `/settings` | `SettingsPage` | Persona global do consultor |
| `/executions`, `/executions/:id` | Redirect → `/` | Rotas legadas desativadas |
| `*` | `NotFoundPage` | 404 |

### Experiência principal (chat)

| Componente / hook | Função |
|-------------------|--------|
| `useChat` | Mensagens, execução ativa, polling 2s, HITL, modo marketing automático |
| `useExecutionActivity` | SSE + poll fallback 3s para timeline |
| `useConversations` | Lista conversas na sidebar |
| `ChatThread`, `ChatComposer` | Thread + input com anexos |
| `ActivitySummaryBar` | Barra colapsável com progresso e previews |
| `MarkdownContent` | Renderiza markdown + blocos `chart`/`kpi` |
| `ChartBlock` | Roteia para gráficos MUI X |

### Gráficos de marketing (`components/marketing/`)

| Componente | `type` |
|------------|--------|
| `FunnelChart` | `funnel` |
| `KpiStrip` | `kpi` |
| `FunnelCompareChart` | `funnel_compare` |
| `BarCompareChart` | `bar_compare` |
| `ProjectionChart` | `projection` |

### Serviços (`services/`)

`agentService`, `conversationService`, `clientService`, `settingsService` — camada fina sobre Axios.

### Variáveis de ambiente (Vite)

| Variável | Default | Descrição |
|----------|---------|-----------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL da API |
| `VITE_API_TIMEOUT_MS` | `30000` | Timeout Axios |

Se `VITE_API_BASE_URL` ausente no build: usa `window.location.origin`.

### Padrões de estilo

- Sem CSS modules — MUI `sx` + overrides de tema (paleta Kyvo indigo/violet)
- Tema claro/escuro persistido em `localStorage` (`manus-theme-mode`)
- Tipografia Inter; locale pt-BR

### Código legado (existe, fora do router)

`HomePage`, `ExecutionsPage`, `ExecutionPage` — dashboard antigo com localStorage; não usadas na UI atual.

---

## Variáveis de ambiente

Fonte: `.env.example` + overrides no `docker-compose.yml`.

| Variável | Default (dev) | Uso |
|----------|---------------|-----|
| `POSTGRES_USER` / `PASSWORD` / `DB` | agent / agent_secret / agent_db | Postgres |
| `DATABASE_URL` | `postgresql+asyncpg://...@localhost:5432/agent_db` | SQLAlchemy + checkpoints |
| `REDIS_URL` | `redis://localhost:6379/0` | Fila, locks, pub/sub |
| `QDRANT_URL` | `http://localhost:6333` | Memória vetorial |
| `QDRANT_COLLECTION` | `agent_memory` | Collection Qdrant |
| `GEMINI_API_KEY` | — | API Gemini (obrigatória) |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Chat |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Embeddings |
| `BROWSER_SERVICE_URL` | `http://localhost:3001` | Playwright |
| `SEARCH_SERVICE_URL` | `http://localhost:8080` | SearXNG |
| `LOG_LEVEL` | `INFO` | Logging |
| `MAX_GRAPH_ITERATIONS` | `10` | Config (critic usa literal `10`) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | CORS FastAPI |
| `ATTACHMENTS_DIR` | `data/attachments` | Diretório de anexos |
| `CLIENT_FILES_DIR` | `data/client-files` | Arquivos de recursos |
| `DEFAULT_AGENT_MODE` | `general` | Default de config |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend build |
| `VITE_API_TIMEOUT_MS` | `30000` | Frontend timeout |

---

## Docker Compose (referência)

```yaml
services:
  postgres:       # postgres:16, volume postgres_data
  redis:          # redis:7, sem porta host
  qdrant:         # :6333, volume qdrant_data
  browser-service: # build ./backend/browser-service, :3001
  search-service:  # searxng/searxng, :8080, settings.yml
  agent-api:       # build ./backend/agent, :8000, volume client_files
  agent-worker:    # mesmo build, command python -m agent.worker
  frontend:        # build ./frontend, :3000→80
```

---

## Testes

Diretório: `backend/agent/tests/` (pytest, `asyncio_mode = auto`).

| Arquivo | Cobertura |
|---------|-----------|
| `test_smoke.py` | Health, AgentState, mock Gemini, search, browser, fila, run, HITL, activity |
| `test_marketing_tools.py` | Ferramentas de marketing |
| `test_marketing_intake.py` | Checklist intake |
| `test_report_formatter.py` | Blocos chart, merge deliverable |
| `test_metrics_auto_detector.py` | Detecção e merge de métricas |
| `test_critic_visual_merge.py` | Merge visual no critic |
| `test_client_config.py` | Contexto de cliente |
| `test_client_service.py` | `build_context_from_client` |
| `test_agent_settings.py` | Persona e validação |
| `test_conversation_context.py` | Histórico e planner |
| `test_execution_client_inherit.py` | Herança de `client_id` |
| `test_file_extractor.py` | Extração de arquivos |

**Lacunas:** E2E do grafo completo, CRUD clients/settings, export PDF, worker Redis real, integração Qdrant/Postgres.

---

## Observabilidade

| Recurso | Estado |
|---------|--------|
| Logs estruturados | `logging_config.py`, nível via `LOG_LEVEL` |
| Timeline de atividades | `execution_activities` + REST + SSE |
| OpenTelemetry / Grafana / Prometheus | **Não implementado** |

---

## Reset do ambiente de desenvolvimento

```powershell
.\scripts\reset-dev.ps1
```

Remove volumes Docker (`postgres_data`, `qdrant_data`, `client_files`), pastas locais de uploads, e sobe o stack com migration inicial. Clientes são cadastrados pela UI em `/clients` (sem seed YAML).

---

## Lacunas e notas de implementação

| Item | Situação atual |
|------|----------------|
| LLM alternativo (OpenAI/Claude) | Abstração existe; só Gemini implementado |
| Observability stack | Não presente no Compose |
| `MAX_GRAPH_ITERATIONS` | Config existe; critic usa `10` hardcoded |
| Rota `research` skip | `next_route` ignorado entre research→critic (arestas fixas) |
| PDF export | Sem renderização de gráficos interativos |
| Frontend legado | `HomePage` / `ExecutionPage` fora do router |
| `@mui/x-data-grid` | Dependência instalada, sem uso em `src/` |
| Mermaid em markdown | Exibe alerta; usar blocos `chart` |

---

## Resumo mental

```text
Docker Compose  = infraestrutura isolada
agent-api       = interface HTTP + enfileiramento
agent-worker    = execução do grafo
LangGraph       = orquestração do fluxo
Gemini          = raciocínio + embeddings
Tools           = browser, search, marketing, memória
Postgres        = estado operacional + checkpoints
Qdrant          = memória semântica
Redis           = fila + eventos em tempo real
Frontend        = chat de consultor + clientes + gráficos markdown
```
