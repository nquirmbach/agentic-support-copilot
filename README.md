# 🤖 Agentic Support Copilot (MVP)

A modern, agentic AI system that turns customer support requests into high‑quality, grounded draft replies using a multi-agent workflow, RAG+, guardrails, and observability.

---

# 🚀 What It Does

1. User pastes a **support message**
2. System runs a multi-agent workflow:
   - Classifier
   - Retriever (RAG+)
   - Writer
   - Guard
   - Logger/Evaluator
3. UI displays:
   - final answer
   - knowledge snippets used
   - full agent trace
   - latency & token metrics

This showcases real-world agent engineering principles.

---

# 🧩 Tech Stack

### Frontend

- Vite + React + TypeScript
- TailwindCSS
- REST API to backend

### Backend

- FastAPI
- LangGraph (preferred) or AutoGen
- Azure OpenAI (chat + embeddings)
- pgvector (Supabase Postgres)

### Monorepo Layout

```
/
├─ apps/
│  ├─ web/            # Vite + React frontend
│  └─ api/            # FastAPI backend (agent orchestration)
├─ infra/             # Local dev scripts (optional)
├─ docs/              # Documentation
│  ├─ CONTEXT.md      # Business & product context
│  └─ ROADMAP.md      # Project roadmap
├─ AGENTS.md          # Agent instructions
└─ README.md          # Human-oriented project description
```

---

# 📦 Features

- Paste any support request
- Multi-agent pipeline
- RAG+ retrieval with pgvector
- Guardrails & moderation
- Trace viewer
- Latency & token metrics

---

# 🧰 Setup

## Backend

```
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Environment variables:

```
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_CHAT_DEPLOYMENT=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
DATABASE_URL=
MODEL_PROVIDER=azure
```

## Frontend

```
cd apps/web
pnpm install
pnpm dev
```

Configure:

```
VITE_API_BASE_URL=http://localhost:8000
```

---

# 📚 Documentation

- **AGENTS.md** – instructions for coding agents
- **docs/CONTEXT.md** – business context
- **docs/ROADMAP.md** – project roadmap
- **README.md** – this file

---

# 🧭 Roadmap

- SSE/WS streaming
- Evaluation suite
- More advanced guardrails
- Multi-user mode
- KB management UI

---

# 🛡️ License

MIT recommended.
