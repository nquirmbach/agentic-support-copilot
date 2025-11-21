# Phase 1 – Structured logging and correlation IDs

## 1. Feature overview

This feature replaces ad-hoc `print` debugging with **structured JSON logging** and introduces **per-request correlation IDs** in the backend.

Goals:

- Emit machine-parseable JSON logs to stdout (friendly for local dev, containers, and future log backends).
- Attach a correlation ID to each `/process` request so all agent and service logs for a given request can be traced.
- Prepare the API for future observability work (e.g., Aspire, OTLP collectors) without locking into any vendor.

## 2. Technical implementation

### 2.1 Logging configuration module

File: `apps/api/src/logging_config.py`

Key pieces:

- `JsonFormatter` – custom `logging.Formatter` that renders each record as a JSON object with:

  - `timestamp` (UTC, ISO‑8601), `level`, `logger`, `message`
  - optional `request_id` (from the logging record or a request-scoped context variable)
  - optional `exception` (formatted stack trace when `exc_info` is present)

- `setup_logging()` – configures the root logger:

  - level: `INFO`
  - handler: `StreamHandler(sys.stdout)` with `JsonFormatter`

- `get_logger(name: str)` – returns a namespaced logger `support_copilot.<name>`.

- Request ID handling:
  - `_request_id_var` – `ContextVar[Optional[str]]` storing the current request ID.
  - `set_request_id(request_id: Optional[str] = None) -> str` – sets and returns a new (or provided) request ID.
  - `get_request_id() -> Optional[str]` – reads the current request ID from context.

### 2.2 API integration

File: `apps/api/src/main.py`

- At import time:

  - Calls `setup_logging()` once.
  - Creates an API logger via `get_logger("api")`.

- In `/process`:
  - Generates a per-request ID using `set_request_id()` at the start of the handler.
  - Logs key lifecycle events with `logger.info(...)`, always including `extra={"request_id": request_id}`:
    - request received
    - validation started / passed
    - workflow invocation completed
  - On unexpected exceptions, uses `logger.exception("FASTAPI workflow error", extra={"request_id": request_id})` before raising a structured 500 error.

The existing success and error response shapes remain the same (structured errors were added in a separate feature).

### 2.3 Agent and service logging

Agents now use their own component loggers:

- `ClassifierAgent` → `get_logger("classifier")`
- `RetrieverAgent` → `get_logger("retriever")`
- `WriterAgent` → `get_logger("writer")`
- `GuardAgent` → `get_logger("guard")`
- `KnowledgeBase` service → `get_logger("knowledge_base")`

Representative changes:

- Classifier:

  - Replaces console `print` calls (e.g. "Starting classification", "Calling LLM", "Parsing JSON response") with `self.logger.info(...)` calls.

- Retriever:

  - Logs the start of retrieval and the call to the knowledge base instead of printing.

- Writer & Guard:

  - Log key milestones (writer response generated, guard validation response received).

- KnowledgeBase:
  - Logs `search_similar` lifecycle events (`search_similar called`, `generating embedding`, `embedding generated successfully`).
  - Logs failures via `self.logger.exception(...)` instead of printing error messages.

Because the API sets the `request_id` context at the start of `/process`, all subsequent logs emitted during that request (in agents, knowledge base, etc.) will carry the same `request_id` via the context-aware formatter.

## 3. Setup instructions

No special setup is required; logging configuration is applied automatically when the API module is imported.

To see logs locally:

1. From `apps/api`, start the server:

   ```bash
   task start
   ```

2. Send one or more `/process` requests.

3. Observe JSON logs on stdout for each request, including the `request_id` field.

## 4. Usage examples

### 4.1 Example log entry

A typical log line (formatted as JSON) will look conceptually like:

```json
{
  "timestamp": "2025-01-01T12:34:56.789Z",
  "level": "INFO",
  "logger": "support_copilot.api",
  "message": "FASTAPI workflow completed",
  "request_id": "<uuid>"
}
```

Errors will additionally include an `exception` field with a formatted stack trace.

### 4.2 Correlating a request

Given a `request_id` from any API log line, you can:

- filter all logs where `request_id` matches that value,
- see the sequence of agent/service logs across classifier, retriever, writer, guard, logger, and knowledge base.

This is particularly useful when debugging slow or failing requests.

## 5. Testing

Recommended checks:

- Start the API and issue several `/process` requests.
- Confirm that:
  - all logs are JSON objects,
  - every log emitted during a single request shares the same `request_id`,
  - agent and knowledge base logs appear under their respective logger names.

When running `task test`, logs will also be emitted; you can optionally suppress or redirect them in the test runner if needed.

## 6. Troubleshooting

- **Logs appear unstructured or duplicated**

  - Ensure no external tooling reconfigures the Python root logger.
  - Check that `setup_logging()` is only called once (it is invoked at import time in `main.py`).

- **Missing request_id in some logs**

  - Confirm that logging for those code paths is executed only after `set_request_id()` is called in the request handler.
  - Background tasks not started from `/process` may legitimately lack a request ID.

- **Too much log noise**
  - Adjust the log level on the root or specific component loggers if necessary (e.g., lower some to `WARNING`).
