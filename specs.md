# 🧠 ESPECIFICAÇÃO COMPLETA — SISTEMA DE AGENTE AUTÔNOMO (Manus-like)

## 🎯 Objetivo

Construir um sistema de agente autônomo baseado em:

* Python + FastAPI (API + runtime do agente)
* LangGraph (orquestração de fluxo)
* LLM via API (OpenAI / Gemini / etc.)
* Arquitetura 100% containerizada
* Serviços desacoplados (cada responsabilidade em um container)

O sistema deve suportar:

* execução de tarefas longas
* uso de ferramentas (browser, search, memory, code execution)
* continuidade de execução (resume de estados)
* human-in-the-loop (pausar e solicitar input humano)
* memória de curto e longo prazo
* observabilidade básica

---

# 🧱 ARQUITETURA DE CONTAINERS (OBRIGATÓRIO: SERVIÇOS SEPARADOS)

O sistema deve ser composto pelos seguintes containers:

---

## 1. 🧠 agent-service (CORE - Python + LangGraph)

### Responsabilidade:

* API principal (FastAPI)
* execução do LangGraph
* orquestração de agentes
* chamada ao LLM
* controle de estado do agente

### Tecnologias:

* Python 3.11+
* FastAPI
* LangGraph
* Pydantic
* HTTP clients para tools

### Exposição:

```text
http://localhost:8000
```

### Endpoints:

* POST /agent/run
* POST /agent/resume/{id}
* POST /agent/continue/{id}
* GET /agent/status/{id}

---

## 2. 🗄️ postgres (STATE STORE)

### Responsabilidade:

* persistência de conversas
* persistência de execução do agente
* checkpoints do LangGraph
* estado de human-in-the-loop

### Uso:

* fonte de verdade do sistema

### Schema mínimo:

* conversations
* messages
* agent_executions
* agent_checkpoints
* human_inputs

### Exposição:

```text
localhost:5432
```

---

## 3. ⚡ redis (QUEUE + EVENT BUS)

### Responsabilidade:

* fila de execução de agentes
* eventos de workflow
* locks distribuídos
* streaming de status

### Uso:

* comunicação entre API e worker
* execução assíncrona

### Exposição:

```text
localhost:6379
```

---

## 4. 🧠 qdrant (VECTOR MEMORY)

### Responsabilidade:

* memória semântica de longo prazo
* embeddings de contexto
* preferências do usuário
* histórico inteligente

### Uso:

* retrieval augmentado (RAG)
* contexto persistente entre sessões

### Exposição:

```text
localhost:6333
```

---

## 5. 🌐 browser-service (PLAYWRIGHT ISOLATED)

### Responsabilidade:

* automação de navegador
* scraping estruturado
* login automation
* interação com sites

### Tecnologias:

* Playwright
* FastAPI (wrapper API)

### Endpoints:

* POST /navigate
* POST /click
* POST /extract
* POST /fill
* POST /screenshot

### Importante:

Este serviço deve ser ISOLADO para evitar:

* crashes no agent core
* bloqueios de execução
* vazamento de sessão

### Exposição:

```text
localhost:3001
```

---

## 6. 🔎 search-service (SearXNG)

### Responsabilidade:

* busca web para o agente
* substituto de Google API
* agregação de resultados

### Exposição:

```text
localhost:8080
```

---

## 7. 📡 observability (OPCIONAL MAS RECOMENDADO)

### Pode incluir:

* OpenTelemetry Collector
* Grafana
* Prometheus

### Responsabilidade:

* rastrear execuções do agente
* logs estruturados
* tracing de tool calls
* debugging de workflows

---

# 🔁 FLUXO DE EXECUÇÃO DO SISTEMA

## Fluxo principal:

```text
User
 ↓
agent-service (FastAPI)
 ↓
Postgres (create execution)
 ↓
Redis queue
 ↓
LangGraph engine
 ↓
LLM (OpenAI/Gemini)
 ↓
Tools:
   - browser-service
   - search-service
   - qdrant
 ↓
Postgres (checkpoint)
 ↓
Response API
```

---

# 🧠 LANGGRAPH DESIGN (OBRIGATÓRIO)

O agente deve ser implementado como um grafo com os seguintes nós:

## Nodes obrigatórios:

* planner_node
* research_node
* browser_node
* tool_execution_node
* memory_node
* critic_node
* human_input_node (PAUSE STATE)

---

## Estado do agente:

```python
AgentState:
  goal: str
  messages: list
  current_step: str
  tool_calls: list
  memory_context: list
  execution_id: str
  status: Running | WaitingHumanInput | Completed | Failed
  pending_question: Optional[str]
```

---

# 🧠 HUMAN-IN-THE-LOOP (OBRIGATÓRIO)

O sistema deve suportar pausa automática quando:

* falta informação crítica
* site exige decisão humana
* múltiplas opções válidas
* ambiguidade de ação

### Comportamento:

1. agente detecta necessidade
2. retorna estado:

```json
{
  "status": "WaitingHumanInput",
  "question": "Qual país devemos priorizar?",
  "options": ["Brasil", "EUA", "Global"]
}
```

3. sistema salva no Postgres
4. aguarda resposta
5. retoma execução no mesmo node

---

# 🧠 MEMORY DESIGN

## Short-term memory (Postgres):

* chat history
* execution state
* tool outputs

## Long-term memory (Qdrant):

* user preferences
* learned facts
* semantic history

---

# 📦 DOCKER COMPOSE (OBRIGATÓRIO)

Todos os serviços devem ser isolados:

```yaml
services:

  agent-service:
    build: ./agent
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - qdrant
      - browser-service
      - search-service

  postgres:
    image: postgres:16
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"

  browser-service:
    build: ./browser-service
    ports:
      - "3001:3001"

  search-service:
    image: searxng/searxng
    ports:
      - "8080:8080"
```

---

# 🧠 REGRAS IMPORTANTES DE DESIGN

## 1. Agent-service é o único cérebro

Nenhum outro serviço decide lógica.

---

## 2. Tools são stateless

Browser, search e memory services NÃO têm inteligência.

---

## 3. Estado sempre persistido

Nenhuma execução pode depender de memória RAM.

---

## 4. Resume obrigatório

O sistema deve suportar:

* restart de container
* retomada de execução
* continuidade de workflow

---

## 5. LLM é substituível

O sistema deve suportar troca entre:

* OpenAI
* Gemini
* Claude

via abstraction layer.

---

# 🚀 RESULTADO FINAL ESPERADO

O sistema deve se comportar como:

* um agente autônomo
* capaz de executar tarefas longas
* capaz de navegar web
* capaz de pedir ajuda humana
* capaz de continuar após dias/semanas
* com memória persistente

---

# 🧭 RESUMO MENTAL

```text
Docker = infraestrutura
FastAPI = interface
LangGraph = cérebro do fluxo
LLM = raciocínio
Tools = corpo (ação)
Postgres = memória operacional
Qdrant = memória inteligente
Redis = sistema nervoso (eventos)
```