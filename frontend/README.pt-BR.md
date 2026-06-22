# Frontend — Interface do Agente Manus-like

SPA React para enviar tarefas ao agente, monitorar execuções e fornecer input humano (human-in-the-loop). Construída com a mesma arquitetura e tema MUI do frontend admin Kyvo.

## Stack

- React 19 + TypeScript 6
- Vite 8
- MUI 9 + Emotion
- React Router 7 (data mode)
- Axios

## Estrutura do projeto

```text
frontend/src/
├── config/         # env.ts, axios.ts
├── contexts/       # ThemeModeContext
├── theme/          # tokens Kyvo + createAppTheme
├── components/
│   ├── ui/         # Primitivos MUI reutilizáveis (do Kyvo)
│   └── AppLayout.tsx
├── services/       # agentService.ts, httpPaths.ts
├── types/
├── utils/
└── pages/          # HomePage, ExecutionsPage, ExecutionPage
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

No Docker, `VITE_API_BASE_URL` é passada como build arg (veja `docker-compose.yml` na raiz).

## Páginas

| Rota | Descrição |
|------|-----------|
| `/` | Dashboard — enviar nova tarefa |
| `/executions` | Lista de execuções recentes (localStorage do navegador) |
| `/executions/:id` | Polling de status, input humano, resume |

## Integração com a API

A interface comunica apenas com `agent-api`:

- `POST /agent/run` — iniciar tarefa
- `GET /agent/status/{id}` — polling a cada 2s na página de execução
- `POST /agent/continue/{id}` — enviar resposta humana
- `POST /agent/resume/{id}` — reenfileirar após interrupção

## Padrões arquiteturais (do Kyvo)

- **Sem CSS personalizado** — apenas `sx` do MUI e overrides do tema
- **Camada de serviços** — chamadas Axios em `services/`, páginas buscam via `useEffect`
- **Primitivos UI** — `PageHeader`, `SectionCard`, `DataTable`, `StatusChip`, etc.
- **Tema** — claro/escuro via `ThemeModeContext`, paleta indigo/violet do Kyvo

## Docker

```bash
docker build -t manus-frontend ./frontend
```

Ou use `docker compose up --build` na raiz para subir o stack completo.
