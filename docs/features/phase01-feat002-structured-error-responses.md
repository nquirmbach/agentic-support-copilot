# Phase 1 – Structured error responses

## 1. Feature overview

This feature introduces **structured error responses** for the `/process` endpoint so callers (frontend, tools, tests) can reliably interpret failures.

Instead of returning plain string messages in `detail`, the API now returns a consistent object with:

- a machine-readable `code`
- a human-friendly `message`

This is a backend-only change; frontend presentation of these errors will be handled in a later Phase 1 frontend task.

## 2. Technical implementation

### 2.1 Error models

File: `apps/api/src/main.py`

New models:

- `ErrorDetail`
  - `code: str`
  - `message: str`
- `ErrorResponse`
  - `error: ErrorDetail`

These models describe the shape of structured errors. For now they are not wired as explicit `response_model` types on the route, but they define the contract used in `HTTPException.detail`.

### 2.2 /process endpoint error payloads

Previously, the `/process` endpoint raised `HTTPException` with plain string `detail` values for:

- validation errors (empty request text)
- internal workflow errors (unexpected exceptions)

Now, it uses structured `detail` objects:

- **Validation error – empty or whitespace-only text**

  ```python
  raise HTTPException(
      status_code=400,
      detail={
          "code": "EMPTY_REQUEST_TEXT",
          "message": "Request text cannot be empty",
      },
  )
  ```

- **Internal error – workflow exception**

  ```python
  raise HTTPException(
      status_code=500,
      detail={
          "code": "WORKFLOW_ERROR",
          "message": "An error occurred while processing your request. Please try again.",
      },
  )
  ```

The success response remains unchanged and still uses `ProcessResponse`.

### 2.3 Tests

File: `apps/api/tests/unit/test_api.py`

Updated tests in `TestProcessEndpoint`:

- `test_process_request_empty_text`

  - Asserts `status_code == 400`.
  - Verifies `data["detail"]` is a dict with:
    - `code == "EMPTY_REQUEST_TEXT"`
    - `message` containing "Request text cannot be empty".

- `test_process_request_whitespace_only`

  - Same assertions as above for whitespace-only requests.

- `test_process_request_workflow_error`
  - Mocks `workflow.process_request` to raise `Exception("Test error")`.
  - Asserts `status_code == 500`.
  - Verifies `data["detail"]` is a dict with:
    - `code == "WORKFLOW_ERROR"`
    - `message` containing "An error occurred while processing your request".

These tests ensure the new structured format is stable and enforced.

## 3. Setup instructions

No additional setup is required beyond running the API as usual.

From `apps/api`:

```bash
task start
```

Then send invalid or error-inducing `/process` requests to see structured errors in responses.

## 4. API / usage examples

### 4.1 Empty request text

Request:

```http
POST /process
Content-Type: application/json

{"request_text": ""}
```

Response (400):

```json
{
  "detail": {
    "code": "EMPTY_REQUEST_TEXT",
    "message": "Request text cannot be empty"
  }
}
```

### 4.2 Internal workflow error

If the internal workflow raises an unexpected exception, the endpoint returns:

```json
{
  "detail": {
    "code": "WORKFLOW_ERROR",
    "message": "An error occurred while processing your request. Please try again."
  }
}
```

The concrete root cause is still logged server-side; the client only gets a safe, user-friendly error.

## 5. Testing

Recommended checks:

- Run unit tests from `apps/api`:

  ```bash
  task test
  ```

- Manually test via a REST client or frontend:
  - Empty or whitespace-only `request_text` → 400 + `EMPTY_REQUEST_TEXT` code.
  - Temporarily mock or misconfigure the workflow to force an exception → 500 + `WORKFLOW_ERROR` code.

## 6. Troubleshooting

- **Client code expects string `detail`**

  - Update callers to handle `detail` as an object with `code` and `message`.

- **Need more granular error codes**

  - Extend the mapping by adding new codes (e.g. `KB_UNAVAILABLE`, `LLM_ERROR`) and corresponding `HTTPException` branches.

- **Want typed error responses in OpenAPI**
  - Optionally add explicit `responses={...}` metadata to the `/process` route, using `ErrorResponse` for 4xx/5xx schemas.
