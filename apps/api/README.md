# Agentic Support API

FastAPI backend for the Agentic Support Copilot.

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create `.env` file:

```env
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.
