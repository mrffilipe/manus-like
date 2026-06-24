# Frontend — Manus-like Agent UI

React SPA for the B2B marketing consultant chat: conversations with client context, resource management, human-in-the-loop, live activity timeline, and interactive charts embedded in markdown reports. Built with the Kyvo MUI architecture.

## Stack

- React 19 + TypeScript 6
- Vite 8
- MUI 9 + Emotion + `@mui/x-charts`
- React Router 7 (data mode)
- Axios
- `react-markdown` + `remark-gfm`

## Project structure

```text
frontend/src/
├── config/              # env.ts, axios.ts
├── contexts/            # ThemeModeContext
├── theme/               # Kyvo tokens + createAppTheme
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
npm run build     # production build
npm run preview   # preview production build
```

## Environment

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Agent API base URL |
| `VITE_API_TIMEOUT_MS` | `30000` | Request timeout |

In Docker, `VITE_API_BASE_URL` is passed as a build arg (see root `docker-compose.yml`). If unset at build time, the app falls back to `window.location.origin`.

## Routes

| Route | Description |
|-------|-------------|
| `/` | New conversation — welcome screen + client selector |
| `/c/:conversationId` | Existing conversation thread |
| `/clients` | List and create marketing clients |
| `/clients/:clientId` | Client profile + resource CRUD |
| `/settings` | Global marketing consultant persona (system prompt) |
| `/executions`, `/executions/:id` | Redirect to `/` (legacy routes) |

## Main flows

**Marketing chat:** when a client is selected, `useChat` sends `agent_mode: marketing_consultant` automatically. The thread polls execution status every 2s; `useExecutionActivity` streams activity via SSE (`/agent/events/{id}`) with polling fallback.

**Human-in-the-loop:** when status is `WaitingHumanInput`, the composer accepts a free-text answer or radio options from `pending_options`.

**Markdown reports:** assistant messages render via `MarkdownContent`. Fenced blocks with language `chart` or `kpi` render interactive MUI X charts (`funnel`, `funnel_compare`, `bar_compare`, `projection`, `kpi`).

## API integration

The UI talks only to `agent-api` through the `services/` layer:

| Area | Key endpoints |
|------|---------------|
| Agent | `POST /agent/run`, `POST /agent/run/upload`, `GET /agent/status/{id}`, `POST /agent/continue/{id}`, `POST /agent/resume/{id}`, `GET /agent/export/{id}/pdf` |
| Activity | `GET /agent/activity/{id}`, `GET /agent/events/{id}` (SSE) |
| Conversations | `GET /agent/conversations`, `GET /agent/conversations/{id}/messages`, `DELETE /agent/conversations/{id}` |
| Clients | `GET/POST/PATCH/DELETE /agent/clients`, resources CRUD + upload + refresh |
| Settings | `GET/PATCH /agent/settings`, `POST /agent/settings/reset` |

## Architecture patterns (from Kyvo)

- **No custom CSS** — MUI `sx` and theme overrides only
- **Service layer** — Axios calls in `services/`; hooks orchestrate state
- **UI primitives** — `PageHeader`, `SectionCard`, `DataTable`, `StatusChip`, etc.
- **Theme** — light/dark via `ThemeModeContext`, Kyvo indigo/violet palette, pt-BR locale

## Docker

```bash
docker build -t manus-frontend ./frontend
```

Or use root `docker compose up --build` to start with the full stack.

See [specs.md](../specs.md) for the full system design.
