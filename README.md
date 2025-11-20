# 🤖 Agentic Support Copilot (MVP)

A modern, agentic AI system that transforms customer support requests into high‑quality, grounded draft replies using a sophisticated multi-agent workflow with RAG+, guardrails, and comprehensive observability.

---

# 🚀 Quick Start

**Get running in 2 minutes with our Taskfile system:**

```bash
# Clone and setup everything automatically
git clone <repo-url>
cd support-copilot
task setup    # Installs all dependencies with validation
task setup-supabase    # Configures Supabase project and knowledge base
task start    # Starts both backend and frontend
```

That's it! Your agentic support system will be running at:

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

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

Our Taskfile system handles everything automatically:

```bash
# Install Task (if you don't have it)
# macOS: brew install go-task/tap/go-task
# Linux: curl -Ls https://taskfile.dev/install.sh | sh

# Clone and setup
git clone <repo-url>
cd support-copilot
task setup    # Validates dependencies and installs everything
task setup-supabase    # Configures Supabase project and knowledge base
task start    # Starts both backend and frontend
```

**What `task setup` does:**

- ✅ Validates Python 3.11+ and Node.js availability
- ✅ Creates virtual environments and installs dependencies
- ✅ Sets up both backend and frontend automatically
- ✅ Provides clear error messages with installation guidance

**What `task setup-supabase` does:**

- 🔧 Installs Supabase CLI if needed
- 🔗 Links your Supabase project interactively
- 📊 Extracts project credentials automatically
- 🗄️ Applies database migrations
- 📝 Updates environment variables in root .env
- 🧪 Tests Supabase connection

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
task setup      # Install all dependencies
task setup-supabase  # Configure Supabase project and knowledge base
task setup-api  # Setup backend only
task setup-web  # Setup frontend only

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

The `task setup-supabase` command automatically configures Supabase credentials in the root `.env` file. For manual setup, create `.env` in the project root:

```bash
# Azure OpenAI (Required for AI features)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# Supabase (Required for knowledge base - auto-configured by setup-supabase)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

**Note:** Supabase credentials should be configured automatically by running `task setup-supabase`. The service role key is required for database operations.

### Azure Infrastructure Setup

Deploy required Azure resources:

```bash
cd infra/azure
task setup    # Validates Azure CLI and Terraform
task deploy   # Deploys Azure OpenAI resources
```

**Prerequisites for Azure setup:**

- Azure CLI installed and logged in
- Terraform installed
- Appropriate Azure permissions

The infrastructure creates:

- Azure OpenAI Service with GPT-4o deployment
- Text embedding deployment for RAG+
- All necessary networking and permissions

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
