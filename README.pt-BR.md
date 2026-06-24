# Manus-like — Sistema de Agente Autônomo

Monorepo para um agente autônomo containerizado com interface React e serviços Python no backend.

## Estrutura do repositório

```text
manus-like/
├── frontend/          # SPA React + MUI (arquitetura Kyvo)
├── backend/
│   ├── agent/         # Core FastAPI + LangGraph
│   ├── browser-service/
│   └── infra/
├── docker-compose.yml
├── specs.md
└── .env.example
```

## Início rápido

1. Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

2. Defina `GEMINI_API_KEY` no `.env`.

3. Suba todos os serviços:

```bash
docker compose up --build
```

4. Acesse a interface:

- **Frontend:** http://localhost:3000
- **API do agente:** http://localhost:8000
- **Docs da API:** http://localhost:8000/docs

## Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `frontend` | 3000 | Interface React |
| `agent-api` | 8000 | API REST do agente |
| `browser-service` | 3001 | Automação Playwright |
| `search-service` | 8080 | Busca web SearXNG |
| `postgres` | 5432 | Estado operacional |
| `redis` | 6379 | Fila de jobs |
| `qdrant` | 6333 | Memória vetorial |

## Documentação

- [README do Frontend](frontend/README.pt-BR.md) | [EN](frontend/README.md)
- [README do Backend](backend/README.pt-BR.md) | [EN](backend/README.md)
- [Especificação do sistema](specs.md)

## Desenvolvimento

**Frontend (local):**

```bash
cd frontend
npm install
npm run dev
```

**Testes do backend:**

```bash
cd backend/agent
pip install -e ".[dev]"
pip install -e "../browser-service"
pytest tests/
```

Consulte os READMEs filhos para detalhes de configuração e uso da API.

## Reset do ambiente de desenvolvimento

Para limpar todos os dados (Postgres, Qdrant, Redis, uploads de arquivos de cliente) e aplicar a migration inicial em banco vazio:

```powershell
.\scripts\reset-dev.ps1
```

O script remove os volumes Docker (`postgres_data`, `qdrant_data`, `client_files`), as pastas locais `backend/agent/data/client-files` e `data/attachments` se existirem, e sobe o stack novamente. Clientes são cadastrados pela UI em `/clients` (sem seed YAML).
