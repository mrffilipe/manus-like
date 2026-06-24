# Frontend — Interface do Agente Manus-like

SPA React para o chat de consultor de marketing B2B: conversas com contexto de cliente, gestão de recursos, human-in-the-loop, timeline de atividade em tempo real e gráficos interativos embutidos em relatórios markdown. Construída com a arquitetura MUI do Kyvo.

## Stack

- React 19 + TypeScript 6
- Vite 8
- MUI 9 + Emotion + `@mui/x-charts`
- React Router 7 (data mode)
- Axios
- `react-markdown` + `remark-gfm`

## Estrutura do projeto

```text
frontend/src/
├── config/              # env.ts, axios.ts
├── contexts/            # ThemeModeContext
├── theme/               # tokens Kyvo + createAppTheme
├── hooks/               # useChat, useConversations, useExecutionActivity
├── components/
│   ├── chat/            # ChatThread, ChatComposer, ActivitySummaryBar
│   ├── activity/        # ActivityTimeline, previews (webpage, search, etc.)
│   ├── marketing/       # ChartBlock, FunnelChart, KpiStrip, etc.
│   ├── clients/         # ResourceCard, ResourceTypeBadge
│   ├── ui/              # MarkdownContent, PageHeader, SectionCard, …
│   └── AppLayout.tsx
├── services/            # agent, conversation, client, settings
├── types/
├── utils/
└── pages/               # ChatPage, ClientsPage, ClientDetailPage, SettingsPage
```

## Scripts

```bash
npm run dev       # http://localhost:3000
npm run build     # build de produção
npm run preview   # preview do build
```

## Ambiente

Copie `.env.example` para `.env`:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | URL base da API do agente |
| `VITE_API_TIMEOUT_MS` | `30000` | Timeout das requisições |

No Docker, `VITE_API_BASE_URL` é passada como build arg (veja `docker-compose.yml` na raiz). Se ausente no build, o app usa `window.location.origin`.

## Rotas

| Rota | Descrição |
|------|-----------|
| `/` | Nova conversa — boas-vindas + seletor de cliente |
| `/c/:conversationId` | Thread de conversa existente |
| `/clients` | Lista e criação de clientes de marketing |
| `/clients/:clientId` | Perfil do cliente + CRUD de recursos |
| `/settings` | Persona global do consultor (system prompt) |
| `/executions`, `/executions/:id` | Redirecionam para `/` (rotas legadas) |

## Fluxos principais

**Chat de marketing:** com cliente selecionado, `useChat` envia `agent_mode: marketing_consultant` automaticamente. A thread faz polling de status a cada 2s; `useExecutionActivity` transmite atividade via SSE (`/agent/events/{id}`) com fallback de polling.

**Human-in-the-loop:** quando o status é `WaitingHumanInput`, o composer aceita resposta em texto livre ou opções via radio de `pending_options`.

**Relatórios markdown:** mensagens do assistente renderizam via `MarkdownContent`. Blocos com linguagem `chart` ou `kpi` exibem gráficos MUI X interativos (`funnel`, `funnel_compare`, `bar_compare`, `projection`, `kpi`).

## Integração com a API

A interface comunica apenas com `agent-api` pela camada `services/`:

| Área | Endpoints principais |
|------|---------------------|
| Agente | `POST /agent/run`, `POST /agent/run/upload`, `GET /agent/status/{id}`, `POST /agent/continue/{id}`, `POST /agent/resume/{id}`, `GET /agent/export/{id}/pdf` |
| Atividade | `GET /agent/activity/{id}`, `GET /agent/events/{id}` (SSE) |
| Conversas | `GET /agent/conversations`, `GET /agent/conversations/{id}/messages`, `DELETE /agent/conversations/{id}` |
| Clientes | `GET/POST/PATCH/DELETE /agent/clients`, CRUD de recursos + upload + refresh |
| Settings | `GET/PATCH /agent/settings`, `POST /agent/settings/reset` |

## Padrões arquiteturais (do Kyvo)

- **Sem CSS personalizado** — apenas `sx` do MUI e overrides do tema
- **Camada de serviços** — chamadas Axios em `services/`; hooks orquestram o estado
- **Primitivos UI** — `PageHeader`, `SectionCard`, `DataTable`, `StatusChip`, etc.
- **Tema** — claro/escuro via `ThemeModeContext`, paleta indigo/violet do Kyvo, locale pt-BR

## Docker

```bash
docker build -t manus-frontend ./frontend
```

Ou use `docker compose up --build` na raiz para subir o stack completo.

Consulte [specs.md](../specs.md) para o design completo do sistema.
