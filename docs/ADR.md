# Architecture Decision Records (ADR)

This document captures key architectural decisions made during the Agentic Support Copilot project.

Each decision is recorded as an ADR section with a consistent structure: Context, Decision, and Consequences.

---

## ADR 0001 – Azure Infrastructure Strategy

**Status**

Accepted

**Date**

2025-11-21

### Context

Early in the project, the repository included a Terraform-based Azure infrastructure module under `infra/azure` that provisioned:

- an Azure AI Foundry hub and project
- a storage account
- a Key Vault
- supporting role assignments

This setup was orchestrated by Taskfile tasks and was intended to give a fully reproducible infra story.

In practice, this introduced several issues:

- The Terraform configuration was tightly coupled to a specific Azure subscription, tenant, and resource layout.
- Provider/resource behavior (e.g. AI Foundry / workspace MSI constraints) caused confusing deployment errors.
- Most contributors still needed to manually adjust Azure resources in the Portal (model deployments, endpoints, etc.).
- The infra code added cognitive and maintenance overhead without clear benefit for the MVP.

At the same time, the core goal of this repository is to showcase the **agentic support copilot** (multi-agent pipeline, RAG, guardrails, observability), not to provide production-ready cloud provisioning.

### Decision

We removed the Terraform-based Azure infrastructure module and switched to **manual Azure setup** as the supported path for this repository.

Concretely:

- The entire `infra/azure` directory (Terraform files, Taskfile, tfvars, etc.) has been deleted.
- Root Taskfile tasks that depended on `infra/azure` have been removed.
- The project documentation (root `README.md` and `docs/features/phase00-feat000-azure-infra.md`) has been updated to:
  - describe Azure resources as **manually provisioned** (Azure OpenAI or Azure AI Foundry)
  - treat the former Terraform setup as historical context only
  - focus the Taskfiles on local development: Supabase, backend, and frontend.

Azure integration is now defined purely via environment variables in the root `.env` file (`OPENAI_ENDPOINT`, `OPENAI_API_KEY`, deployment names, etc.).

### Consequences

**Positive**

- Lower maintenance cost: no Terraform code to keep in sync with evolving Azure providers and services.
- Simpler onboarding: new contributors follow a straightforward manual Azure setup in the Portal plus Taskfile-based local setup.
- Clearer project scope: the repo focuses on the multi-agent application and local dev flow, not on cloud provisioning.
- Fewer failure modes: we avoid subtle provider/resource bugs blocking local experimentation.

**Negative**

- No in-repo reproducible infra: teams that want full IaC for Azure must manage it in a separate project or layer.
- Manual Azure steps required: contributors must be comfortable with the Azure Portal (or their own scripts) to create the AI resource and deployments.

**Mitigations / Future Options**

- If strong need arises, we can reintroduce IaC as a separate, optional module or companion repo, with clearer ownership and testing.
- The existing documentation explicitly documents required Azure resources and environment variables, so external IaC can target that contract.

---

_To add future decisions, append new sections here (e.g. `ADR 0002 – LLM Provider Abstraction`, `ADR 0003 – Multi-Agent Orchestration Framework`, etc.)._
