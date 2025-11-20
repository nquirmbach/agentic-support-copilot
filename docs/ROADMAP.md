# ROADMAP.md

This roadmap provides a **long‑term strategic overview** for the Agentic Support Copilot.  
It outlines phases from a minimal MVP to a robust agentic AI platform aligned with modern AI engineering practices.

---

# 📍 Phase 0 — Foundation (Current) 🚧 IN PROGRESS

**Goal:** Establish a minimal but complete agentic workflow.

### Deliverables

- Multi-agent pipeline (Classifier → Retriever → Writer → Guard → Logger)
- Supabase pgvector knowledge base
- Simple FastAPI backend
- Vite + React frontend
- One `/process` endpoint
- Azure OpenAI integration
- Basic metrics: latency, token usage
- Trace visualization in UI

**Outcome:** Fully functional minimal agentic system.

---

# 🚀 Phase 1 — Productizing the MVP

**Goal:** Improve robustness, reliability, configurability.

### Backend

- Add retries + timeout handling for agent steps
- Add configurable prompts per agent
- Add structured error responses
- Add better logging (structured logs)

### Frontend

- Improve UI/UX
- Better trace visualization (timeline / step cards)
- Highlight which KB snippets were used

### Knowledge Base

- Add small UI to view KB entries
- Add ability to disable low-scoring snippets (RAG+ threshold tuning)

**Outcome:** MVP feels stable and pleasant to use.

---

# 🧠 Phase 2 — RAG+ Enhancements

**Goal:** Improve retrieval quality and context grounding.

### Retrieval Improvements

- Add semantic reranking step (LLM or scoring model)
- Add document prioritization (policies > FAQ > long texts)
- Add answer verification agent
- Add “reference checking” prompt to detect hallucinations

### KB Improvements

- Add multi-field embeddings (title + content)
- Auto-tagging suggestions
- Embedding versioning

**Outcome:** Higher-quality answers with strong grounding and fewer hallucinations.

---

# 🔒 Phase 3 — Guardrails & Moderation

**Goal:** Expand safety, correctness, and compliance.

### Guardrails Engine

- Add schema validators using Guardrails AI
- Add policy checks (e.g., never offer refunds over X €)
- Add profanity check, PII detection
- Add “red flag” warnings in UI

### Multi-step Guard Agent Flow

- If guard fails → auto-revision loop with writer agent
- Add audit log for safety events

**Outcome:** Safe and policy-aligned agent behavior.

---

# 📊 Phase 4 — Observability & Evaluation

**Goal:** Measure quality, reliability, and cost.

### Observability

- Integrate with Phoenix or Langfuse
- Add spans for each agent step
- Capture:
  - P50/P95 latency
  - token usage
  - model cost estimates
  - failure rate per agent

### Evaluation

- Create a dataset of synthetic support tickets
- Add evaluation pipeline:
  - correctness
  - helpfulness
  - groundedness
  - hallucination rate

### Reporting

- Add simple dashboard: “System Health & Quality”

**Outcome:** A measurable and improvable system.

---

# 🛠️ Phase 5 — Tooling & Agent-to-Agent (A2A)

**Goal:** Expand agent capabilities.

### Features

- Multiple specialized writer agents (e.g., “refund expert”, “tech support”)
- Router agent to pick correct sub-agent
- Agent-to-agent communication via structured messages
- Model Context Protocol (MCP) integration (expose KB or tools as MCP resources)
- Experimental planning agent

**Outcome:** More complex, flexible agent ecosystems.

---

# ⚡ Phase 6 — Real-Time Interaction

**Goal:** Make the system feel alive.

### Backend

- Convert `/process` to Server-Sent Events (SSE) or WebSockets
- Stream: tokens, agent-step events, partial trace

### Frontend

- Real-time token streaming
- “Agent is thinking…” animations
- Live agent step indicators

**Outcome:** Smooth, modern, real-time agent UX.

---

# 🌐 Phase 7 — Knowledge Editing & Multi-Modal Inputs

**Goal:** Increase usefulness & domain coverage.

### Knowledge Editor

- Add full KB CRUD UI
- Import/export KB entries
- Tagging, categorization, versioning

### Multi-modal

- Allow attachment of:
  - screenshots (OCR)
  - PDFs
  - emails (HTML parsing)

**Outcome:** More powerful, real-world support use cases.

---

# 🏢 Phase 8 — Multi-User / SaaS Direction (Optional)

**Goal:** Prepare system for real deployments.

### Features

- User accounts & roles (agent vs admin)
- Team workspaces
- Shared KB spaces
- Usage analytics
- Billing (Stripe)
- Deployable cloud architecture

**Outcome:** The system becomes a production-ready SaaS.

---

# 🎯 Long-Term Vision

A fully-featured **Agentic Support Platform**:

- Multi-agent orchestration
- RAG+ with verifiable grounding
- Guardrails & safety engines
- Rich observability & eval suite
- Real-time UX
- Multi-modal inputs
- Extensible via tools & MCP
- Configurable by domain (industry templates)

A showcase-level project demonstrating cutting-edge AI engineering.
