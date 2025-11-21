# Phase 0 - Feature 0: Infrastructure Prerequisites ✅ UPDATED

## Summary

The initial version of this project used Terraform to provision Azure AI Foundry-based infrastructure (hub + project, storage account, and Key Vault). That Terraform-based setup has been removed.

The current approach is:

- Azure resources (Azure OpenAI or Azure AI Foundry) are created **manually** in the Azure Portal.
- This document now serves as a requirements and guidance reference for what needs to exist in Azure for the Agentic Support Copilot to function.

## What Was Implemented

### Required Azure Resources (Manual Setup)

- **Azure AI resource**: Either Azure OpenAI or Azure AI Foundry exposing an OpenAI-compatible endpoint
- **Model deployments**: At least one chat model (e.g. `gpt-4o`, `gpt-4o-mini`) and one embedding model (e.g. `text-embedding-3-large`)
- **Resource Group**: Container for all Azure resources
- **(Optional) Storage Account / Key Vault**: If you want to mirror the original architecture, you can add storage and Key Vault for artifacts and secrets, but they are not required by this repo.

### How the Backend Uses Azure

- The backend expects an **OpenAI-compatible endpoint** and API key.
- These are provided via the `OPENAI_ENDPOINT` and `OPENAI_API_KEY` variables in the root `.env` file.
- Deployment names for chat and embeddings are provided via:
  - `OPENAI_DEPLOYMENT_NAME`
  - `OPENAI_FAST_DEPLOYMENT_NAME`
  - `OPENAI_EMBEDDING_DEPLOYMENT_NAME`

### Automation Features (Current State)

- No Terraform or Azure IaC is shipped with this repo anymore.
- Taskfiles only handle **local setup** (backend, frontend, Supabase) and assume Azure has been configured manually.

## Technical Decisions

1. **Manual Azure Setup**: Azure resources are managed outside this repo (via Azure Portal, CLI, or an external IaC project).
2. **Local Execution**: This repo focuses on local development of the multi-agent system.
3. **Environment-Driven Config**: All Azure integration is configured via environment variables, not Terraform outputs.

## Historical Note

Earlier iterations of this project included an `infra/azure` folder with Terraform configuration and a dedicated Taskfile. Those files have been removed to keep the repo focused on the application itself.

## Usage Instructions (Manual Azure Setup)

1. In the Azure Portal, create an Azure OpenAI or Azure AI Foundry resource.
2. Create at least one chat model deployment and one embedding deployment.
3. Copy the endpoint and API key into the root `.env` as `OPENAI_ENDPOINT` and `OPENAI_API_KEY`.
4. Set deployment names in `OPENAI_DEPLOYMENT_NAME`, `OPENAI_FAST_DEPLOYMENT_NAME`, and `OPENAI_EMBEDDING_DEPLOYMENT_NAME`.
5. Follow the root `README.md` to configure Supabase and run the backend/frontend.

## Cost Considerations

- **GPT-4**: ~$0.03 per 1K input tokens + $0.06 per 1K output tokens
- **Embeddings**: ~$0.0001 per 1K tokens
- **Resource Group**: No additional cost
- **Monitoring**: Azure Portal usage tracking available

## Integration with Existing System

- Seamless integration with existing FastAPI backend
- Environment variable format matches existing `.env` structure
- Demo mode fallback when Azure credentials not configured
- No changes required to existing agent code

## Status: ✅ COMPLETED (MANUAL SETUP)

Infrastructure prerequisites are documented and must be created manually in Azure. This repo does not include Terraform or other Azure IaC.

## Next Steps

1. Create or verify required Azure resources (Azure OpenAI / Azure AI Foundry) in the Azure Portal.
2. Configure environment variables in the root `.env` (and propagate to `apps/api/.env` via `task setup-api`).
3. Set up the Supabase knowledge base.
4. Test the complete end-to-end system locally.
