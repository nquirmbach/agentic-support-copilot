# Phase 1 – Configurable agent prompts

## 1. Feature overview

This feature makes system prompts for the main LLM‑driven agents **configurable** without code changes.

Agents affected:

- `ClassifierAgent` – intent, sentiment, urgency classification.
- `WriterAgent` – grounded support reply generation.
- `GuardAgent` – safety, hallucination, and policy validation.

Each agent now reads its system prompt from a central `prompts` module, which in turn can be overridden via environment variables.

## 2. Technical implementation

### 2.1 Prompts module

File: `apps/api/src/prompts.py`

Defines three prompt constants with environment overrides:

- `CLASSIFIER_SYSTEM_PROMPT`
- `WRITER_SYSTEM_PROMPT`
- `GUARD_SYSTEM_PROMPT`

Example (defaults, simplified):

- Classifier: detailed instructions for mapping support requests to `intent`, `sentiment`, `urgency`, returned as JSON.
- Writer: instruction to produce a professional, empathetic, grounded support reply using provided knowledge sources.
- Guard: instruction to return JSON `{ is_safe, issues[], confidence }` based on harmful content, hallucinations, and policy checks.

Implementation pattern:

```python
CLASSIFIER_SYSTEM_PROMPT = os.getenv(
    "CLASSIFIER_SYSTEM_PROMPT",
    "... default classifier prompt ...",
)
```

The same pattern is used for `WRITER_SYSTEM_PROMPT` and `GUARD_SYSTEM_PROMPT`.

### 2.2 Agent integration

Files:

- `apps/api/src/agents/classifier.py`
- `apps/api/src/agents/writer.py`
- `apps/api/src/agents/guard.py`

Key changes:

- `ClassifierAgent`:

  - Imports `CLASSIFIER_SYSTEM_PROMPT` from `..prompts`.
  - Uses `system_prompt = CLASSIFIER_SYSTEM_PROMPT` before calling `llm.chat`.

- `WriterAgent`:

  - Imports `WRITER_SYSTEM_PROMPT` from `..prompts`.
  - Uses `system_prompt = WRITER_SYSTEM_PROMPT` for the writer LLM call.

- `GuardAgent`:
  - Imports `GUARD_SYSTEM_PROMPT` from `..prompts`.
  - Uses `system_prompt = GUARD_SYSTEM_PROMPT` for the validator LLM call.

All other behavior (trace structure, state updates, fallbacks) remains unchanged.

## 3. Setup instructions

1. Ensure the API `.env` is present (root or `apps/api/.env`).
2. Optionally override any of the system prompts:

   ```env
   CLASSIFIER_SYSTEM_PROMPT="You are a classifier specialized in billing and refunds..."
   WRITER_SYSTEM_PROMPT="You are a concise, friendly support assistant..."
   GUARD_SYSTEM_PROMPT="You are a strict safety and policy validator..."
   ```

3. Start the API from `apps/api`:

   ```bash
   task start
   ```

4. Send a request to `POST /process` and inspect the answer, trace, and guard output to validate the updated behavior.

## 4. API / usage examples

### 4.1 Tailoring classification behavior

By changing `CLASSIFIER_SYSTEM_PROMPT`, you can:

- bias intents toward your domain‑specific categories,
- adjust sentiment detection examples,
- redefine what counts as high vs medium urgency.

The `ProcessResponse` JSON shape does not change; only the semantics of `intent`, `sentiment`, and `urgency` may shift according to your prompt.

### 4.2 Adjusting writing style

Updating `WRITER_SYSTEM_PROMPT` lets you:

- enforce stricter tone requirements (formal vs casual),
- require bullet‑point answers,
- emphasize certain policies or knowledge sources.

Again, the `answer` field in `/process` remains a string; the prompt only affects style and content.

### 4.3 Tightening guardrails

With `GUARD_SYSTEM_PROMPT` you can:

- add explicit company policies (e.g. refund limits, data‑sharing constraints),
- specify categories of disallowed content,
- tune what should be included in `issues` and how strict `is_safe` should be.

The guard agent still returns parsed JSON with `is_safe`, `issues`, and `confidence` (with fallbacks on parse errors).

## 5. Testing

Recommended checks:

- **Unit / lightweight tests**

  - Set simple override prompts in a dedicated test `.env`.
  - Call each agent in isolation (or via the workflow) and verify that:
    - the LLM call receives the overridden `system` text,
    - the pipeline still produces valid `AgentState` and trace entries.

- **End‑to‑end**
  - Run `task test` in `apps/api` to ensure existing API tests pass with default prompts.
  - Manually call `/process` with:
    - a neutral support request,
    - an obviously high‑urgency request,
    - a potentially unsafe request.
  - Confirm differences in classification, writing, and guard behavior when you change the env prompts.

## 6. Troubleshooting

- **Prompt changes have no effect**

  - Ensure the environment variables are set in the same context that runs the API (e.g. terminal session, container env).
  - Restart the FastAPI server after changing `.env` so new values are loaded.

- **Unexpected JSON from classifier or guard**

  - Very long or complex prompts can cause the model to deviate from strict JSON.
  - Keep the structure instructions for JSON concise and prominent near the end of the prompt.

- **Inconsistent behavior between environments**
  - Verify that each environment (local, staging, prod) has the correct prompt overrides.
  - Consider versioning your prompts in configuration management if they become critical.
