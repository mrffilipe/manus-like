# Frontend — Manus-like Agent UI

React SPA for submitting agent tasks, monitoring executions, and providing human-in-the-loop input. Built with the same architecture and MUI theme as the Kyvo admin frontend.

## Stack

- React 19 + TypeScript 6
- Vite 8
- MUI 9 + Emotion
- React Router 7 (data mode)
- Axios

## Project structure

```text
frontend/src/
├── config/         # env.ts, axios.ts
├── contexts/       # ThemeModeContext
├── theme/          # Kyvo tokens + createAppTheme
├── components/
│   ├── ui/         # Reusable MUI primitives (from Kyvo)
│   └── AppLayout.tsx
├── services/       # agentService.ts, httpPaths.ts
├── types/
├── utils/
└── pages/          # HomePage, ExecutionsPage, ExecutionPage
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

In Docker, `VITE_API_BASE_URL` is passed as a build arg (see root `docker-compose.yml`).

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard — submit new agent goal |
| `/executions` | List recent executions (browser localStorage) |
| `/executions/:id` | Poll status, human input, resume |

## API integration

The UI talks only to `agent-api`:

- `POST /agent/run` — start task
- `GET /agent/status/{id}` — poll every 2s on execution page
- `POST /agent/continue/{id}` — submit human answer
- `POST /agent/resume/{id}` — re-enqueue after interruption

## Architecture patterns (from Kyvo)

- **No custom CSS** — MUI `sx` and theme overrides only
- **Service layer** — Axios calls in `services/`, pages fetch via `useEffect`
- **UI primitives** — `PageHeader`, `SectionCard`, `DataTable`, `StatusChip`, etc.
- **Theme** — light/dark via `ThemeModeContext`, Kyvo indigo/violet palette

## Docker

```bash
docker build -t manus-frontend ./frontend
```

Or use root `docker compose up --build` to start with the full stack.
