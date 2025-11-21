# Agentic Support API

FastAPI backend for the Agentic Support Copilot.

## Setup

```bash
# From the repo root you can run:
# task setup-app   # sets up backend and frontend

# Or from this folder (apps/api):
cd apps/api
task setup   # create venv, install deps, copy .env
task start   # start FastAPI on http://localhost:8000
```

## Environment Variables

Create `.env` file in `apps/api/`:

```env
# OpenAI / Foundry endpoint
OPENAI_ENDPOINT=your_openai_or_foundry_endpoint_url
OPENAI_API_KEY=your_openai_or_foundry_api_key

# Chat models
OPENAI_DEPLOYMENT_NAME=gpt-4o
OPENAI_FAST_DEPLOYMENT_NAME=gpt-4.1-mini

# Embeddings
OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_role_key
```

## Utility Scripts

From the `apps/api` directory you can run several helper scripts:

```bash
cd apps/api

# (Re)seed the Supabase knowledge base with sample articles
python -m scripts.setup_kb

# Clean all documents from the knowledge base
python -m scripts.clean_kb

# Test Supabase + embeddings (DB connection, retrieval, vector search)
python -m scripts.test_kb

# Visualize the AgentWorkflow and create the workflow diagram
python -m scripts.visualize_workflow

# Run the full AgentWorkflow in isolation (without FastAPI)
python -m scripts.test_workflow
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.
