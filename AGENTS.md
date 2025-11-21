# AGENTS.md

This file provides **agent-focused technical guidance** for working on this repository.
It complements the human-oriented `README.md` and the business-focused `CONTEXT.md`.

Agents must follow this document when generating, modifying, or structuring code.

---

# 📦 Project Summary (for Agents)

This repository contains an MVP for an **Agentic Support Copilot**.

The system takes a user-provided **support request** (e.g., ticket, email) and runs it through a **multi-agent pipeline** consisting of:

1. **Classifier Agent** – identifies intent, sentiment, urgency.
2. **Retriever Agent (RAG+)** – fetches relevant knowledge snippets from a small KB.
3. **Writer Agent** – drafts a grounded response.
4. **Guard Agent** – validates safety, hallucinations, and compliance.
5. **Logger/Evaluator** – stores traces, metrics, and basic quality flags.

The result displayed in the UI includes:

- final answer
- used knowledge sources
- full agent trace
- metrics (latency, token usage)

---

# 🏗️ Monorepo Structure

Agents must generate and maintain code in this structure:

```
/
├─ apps/
│  ├─ web/            # Vite + React frontend
│  └─ api/            # FastAPI backend (agent orchestration)
├─ infra/             # Local dev scripts (optional)
├─ supabase/          # Supabase setup and migrations
├─ docs/              # Documentation
│  ├─ CONTEXT.md      # Business & product context
│  └─ ROADMAP.md      # Project roadmap
├─ AGENTS.md          # Agent instructions
└─ README.md          # Human-oriented project description
```

---

# ⚙️ Backend Guidelines (FastAPI + Python)

### Requirements

- Python 3.11+
- Use **FastAPI** (async).
- Implement a **multi-agent workflow** using **LangGraph** (preferred) or AutoGen.
- Use **Azure OpenAI** as the default model provider.
- All LLM calls must go through an abstraction:

```python
class LlmProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...
    async def chat(self, messages: list[dict]) -> str:
        ...
```

### Agents

Implement at minimum:

1. **Classifier Agent**
2. **Retriever Agent (RAG+)**
3. **Writer Agent**
4. **Guard Agent** (safety, hallucinations, policy compliance)
5. **Logger/Evaluator Node**

### Knowledge Base

- Small curated KB (5–20 articles), stored in Postgres or Markdown files.
- Each document must have: title, content, and embeddings.

### Vector Search

- Use **pgvector** in Supabase.
- Always use parameterized SQL.
- Apply relevance thresholds.

---

# 🖥️ Frontend Guidelines (Vite + React)

Requirements:

- Vite + React + TypeScript.
- UI must include:
  - input box for request text
  - button “Generate Answer”
  - final answer display
  - sources used
  - full agent trace timeline
  - metrics (latency, token count)
- Use TailwindCSS.
- API communication via REST.

---

# 🌐 API Endpoint (MVP)

### `POST /process`

**Input**

```json
{
  "request_text": "string"
}
```

**Output**

```json
{
  "answer": "string",
  "sources": [...],
  "trace": [...],
  "metrics": {
    "latency_ms": 0,
    "token_usage": 0
  }
}
```

This endpoint executes the full agent pipeline.

---

# 🚫 Non-Goals

Agents must NOT implement:

- File/PDF/media ingestion
- Next.js
- Multi-user features
- Advanced KB tools
- External services besides Supabase & Azure OpenAI

---

# ✔️ Completion Criteria

The agent's work is complete when:

- `/process` endpoint works end-to-end
- Multi-agent pipeline implemented
- RAG+ retrieval works
- Guardrails integrated
- Trace + metrics returned
- Frontend displays all results
