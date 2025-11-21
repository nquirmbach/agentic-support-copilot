# 🤖 Agentic Support Copilot (MVP)

A modern, agentic AI system that transforms customer support requests into high‑quality, grounded draft replies using a sophisticated multi-agent workflow with RAG+, guardrails, and comprehensive observability.

---

# 🚀 Quick Start

**Get running with a guided Taskfile-based setup (with manual Azure & Supabase steps):**

```bash
# Clone the repo
git clone <repo-url>
cd support-copilot

# 1) Manually create your Azure AI resource (Azure OpenAI or Azure AI Foundry) and note the endpoint, API key and deployment names

# 2) Configure Supabase project and knowledge base
task setup-supabase

# 3) Setup backend & frontend dependencies
task setup-app

# 4) Start both backend and frontend
task start
```

During this process you will:

- Use the Azure Portal to create your Azure AI resource (Azure OpenAI or Azure AI Foundry) and configure chat + embedding deployments
- Edit the root `.env` file with your `OPENAI_*` and `SUPABASE_*` values (see configuration section below)
- Let `task setup-app` copy the root `.env` into `apps/api/.env`

**Current Status:**

- ✅ Infrastructure & Knowledge Base: Ready
- 🚧 Multi-Agent Pipeline: In Development
- 🚧 API Backend & Frontend: In Development

---

# 🎯 What It Does

1. **User Input**: Paste any customer support request
2. **Multi-Agent Processing**:
   - 🏷️ **Classifier** - Identifies intent, sentiment, urgency
   - 🔍 **Retriever (RAG+)** - Fetches relevant knowledge from vector database
   - ✍️ **Writer** - Drafts grounded, contextual responses
   - 🛡️ **Guard** - Validates safety, hallucinations, compliance
   - 📊 **Logger/Evaluator** - Tracks metrics and quality
3. **Rich Output**:
   - Final AI-generated response
   - Knowledge sources used (with citations)
   - Complete agent execution trace
   - Performance metrics (latency, token usage)

This demonstrates production-ready agent engineering with real-time observability.

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

# 🛠️ Setup & Development

## 🚀 Quick Setup (Recommended)

Our Taskfile system orchestrates the setup but still expects **manual Azure & Supabase steps**:

```bash
# Install Task (if you don't have it)
# macOS: brew install go-task/tap/go-task
# Linux: curl -Ls https://taskfile.dev/install.sh | sh

# Clone and enter the repo
git clone <repo-url>
cd support-copilot

# 1) Configure Supabase project & knowledge base
task setup-supabase

# 2) Setup backend & frontend
task setup-app

# 3) Start the system
task start
```

**What these tasks do:**

- **Manual Azure setup (outside Taskfile)**:
  - in the Azure Portal, create an Azure OpenAI / Azure AI Foundry resource
  - create chat + embedding deployments
  - copy the standardized OpenAI-compatible endpoint & API key
  - edit the root `.env` with `OPENAI_*` values (see below)
- **`task setup-supabase`**:
  - configures your Supabase project and applies migrations
  - prints Supabase URL and service role key so you can paste them into the root `.env`
- **`task setup-api`** (in `apps/api`):
  - creates the Python virtual environment
  - installs backend dependencies
  - copies the root `.env` into `apps/api/.env`
- **`task setup-web`** (in `apps/web`):
  - checks Node.js
  - installs frontend dependencies

**What `task setup-supabase` does:**

- 🔧 Installs Supabase CLI if needed
- 🔗 Links your Supabase project interactively
- 📊 Extracts project credentials automatically
- 🗄️ Applies database migrations
- 📝 Prints Supabase URL and service role key for you to copy into the root .env
- 🧪 (Optional) You can run the provided knowledge base tests afterwards to validate connectivity

**What `task start` does:**

- 🚀 Starts FastAPI backend on http://localhost:8000
- 🚀 Starts React frontend on http://localhost:3000
- 🚀 Opens API documentation in your browser

## 📋 Available Commands

```bash
# Development
task start      # Start all apps
task dev        # Start with debug logging
task health     # Check if services are running
task docs       # Open documentation

# Setup
task setup-supabase  # Configure Supabase project and knowledge base
task setup-app  # Setup backend and frontend

# Individual Components
task start-api  # Start backend only
task start-web  # Start frontend only

# Utilities
task stop       # Stop all services
task clean      # Clean all generated files
task lint       # Run linting and formatting
task test       # Run tests
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

## ⚙️ Configuration

### Required Environment Variables

The `task setup-supabase` command helps you retrieve your Supabase credentials; you then add them to the root `.env` file manually. For manual setup without the task, create `.env` in the project root:

```bash
# OpenAI-compatible endpoint from Azure AI Foundry (Required for AI features)
OPENAI_ENDPOINT=https://your-foundry-project.openai.azure.com/
OPENAI_API_KEY=your-api-key

# Deployment names used by the backend (must match your AI Foundry deployments)
OPENAI_DEPLOYMENT_NAME=gpt-4o
OPENAI_FAST_DEPLOYMENT_NAME=gpt-4o-mini
OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large

# Supabase (Required for knowledge base - auto-configured by setup-supabase)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

**Note:**

- Supabase credentials must be pasted into the root `.env` file (the `task setup-supabase` task prints the correct values for you).
- The `OPENAI_*` values must be taken from your Azure AI Foundry project (standardized OpenAI endpoint and deployments).

### Azure Infrastructure Setup

This repository no longer provisions Azure resources automatically. You must:

- Create an Azure OpenAI or Azure AI Foundry resource in the Azure Portal
- Create model deployments (chat + embeddings)
- Use the resulting endpoint, API key and deployment names in the `OPENAI_*` variables of the root `.env` file

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
