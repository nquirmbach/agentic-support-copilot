# Phase 1 – Agent retries and timeouts

## 1. Feature overview

This feature makes the multi‑agent pipeline more robust by adding configurable **retries** and **per‑step timeouts** around each agent call in the LangGraph workflow.

If an agent (Classifier, Retriever, Writer, Guard, Logger) fails transiently or hangs, the workflow will:

- retry the step a limited number of times, and
- abort the step after a configurable timeout.

Failures are recorded in the trace so the frontend and logs can show where the pipeline degraded.

## 2. Technical implementation

### 2.1 Configuration

File: `apps/api/src/config.py`

- `AGENT_MAX_RETRIES` – max number of attempts per agent step (default: `2`).
- `AGENT_STEP_TIMEOUT_SECONDS` – timeout per agent step in seconds (default: `30`).

All values are read from environment variables with sensible defaults, so they can be tuned without code changes.

### 2.2 Workflow retries and timeout

File: `apps/api/src/agents/workflow.py`

- Adds a private helper `_wrap_agent(agent_name, step_name, func)`.
- Each agent node in the LangGraph `StateGraph` is registered through this wrapper.
- Each node is configured with a LangGraph `RetryPolicy(max_attempts=AGENT_MAX_RETRIES)`.

Core behavior:

- `_wrap_agent` executes the underlying async agent function via `asyncio.wait_for(func(state), timeout=AGENT_STEP_TIMEOUT_SECONDS)`.
- If the wrapped call raises (including `asyncio.TimeoutError`), LangGraph's `RetryPolicy` will transparently re‑invoke the node up to `AGENT_MAX_RETRIES` times.
- Individual agents remain responsible for adding success/error `AgentStep` entries into the trace; LangGraph handles the retry orchestration.

### 2.3 Wrapped nodes

The following nodes are now wrapped and have a retry policy applied:

- `classify` → `ClassifierAgent.classify`
- `retrieve` → `RetrieverAgent.retrieve`
- `write` → `WriterAgent.write_response`
- `validate` → `GuardAgent.validate_response`
- `log` → `LoggerAgent.log_and_evaluate`

This keeps all retry/timeout policy in orchestration, without changing individual agent logic.

## 3. Setup instructions

1. Ensure the API app is configured with a `.env` file (either at repo root or `apps/api/.env`).
2. Optionally set the retry/timeout env vars:

   ```env
   AGENT_MAX_RETRIES=2
   AGENT_RETRY_BACKOFF_MS=200
   AGENT_STEP_TIMEOUT_SECONDS=30
   ```

3. Start the API from `apps/api`:

   ```bash
   task start
   ```

4. Use the frontend or `curl` to call `POST /process` with a realistic support request.

## 4. API / usage examples

### 4.1 Normal request

- Endpoint: `POST /process`
- Input body:

  ```json
  { "request_text": "I forgot my password and cannot log in." }
  ```

- Behavior:
  - Each agent step runs once if it succeeds within the timeout.
  - The response includes a full trace and metrics as before.

### 4.2 Simulated transient failure

If an underlying dependency (e.g. OpenAI, Supabase) throws intermittently, the wrapper will:

- retry the failing agent up to `AGENT_MAX_RETRIES`,
- record the final error in `trace` if all attempts fail.

The `/process` endpoint still returns a structured response; downstream features (e.g. structured errors) can build on this trace.

## 5. Testing

Recommended checks:

- **Unit tests**

  - Mock an agent to raise on the first call and succeed on the second.
  - Assert that `_wrap_agent` invokes the function twice and that only one step appears in the trace.

- **Timeout behavior**

  - Mock an agent to sleep longer than `AGENT_STEP_TIMEOUT_SECONDS`.
  - Assert that the wrapper retries and finally records an error step with an `attempts` count.

- **End‑to‑end**
  - Run `task test` in `apps/api` to ensure existing API tests still pass.
  - Manually call `/process` and inspect the `trace` when upstream services are misconfigured (e.g. invalid API key) to verify error steps are recorded.

## 6. Troubleshooting

- **Agent steps never retry**

  - Confirm `AGENT_MAX_RETRIES` is greater than `0` in the environment.
  - Check that the failure is actually raising an exception (silent logical errors will not trigger retries).

- **Requests hang for too long**

  - Lower `AGENT_STEP_TIMEOUT_SECONDS` to fail fast.
  - Reduce `AGENT_MAX_RETRIES` or `AGENT_RETRY_BACKOFF_MS`.

- **Trace does not show error details**

  - Ensure you inspect the last `AgentStep` entries in `trace` for each agent.
  - Confirm that the error is not being swallowed inside the agent implementation; it must propagate so the wrapper can handle it.

- **Increased latency due to retries**
  - Balance resilience and latency by tuning max retries and backoff.
  - For low‑latency environments, prefer fewer retries and shorter timeouts.
