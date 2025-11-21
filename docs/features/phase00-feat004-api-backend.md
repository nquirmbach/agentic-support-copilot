# Phase 0 - Feature 004: API Backend

## Feature Overview

This feature implements the FastAPI backend that serves as the REST API interface for the Agentic Support Copilot. The backend provides endpoints for processing support requests through the multi-agent pipeline, health monitoring, and comprehensive API documentation.

The API backend enables:

- **RESTful Interface**: Clean HTTP endpoints for frontend integration
- **Request Processing**: Seamless integration with the multi-agent pipeline
- **Error Handling**: Comprehensive validation and graceful error responses
- **CORS Support**: Cross-origin requests for frontend applications
- **Health Monitoring**: System health checks and status reporting
- **Auto-documentation**: Interactive OpenAPI/Swagger documentation

## Technical Implementation

### Core Architecture

#### 1. FastAPI Application (`src/main.py`)

- **Application Setup**: FastAPI instance with metadata and versioning
- **Middleware Configuration**: CORS middleware for frontend integration
- **Endpoint Routing**: RESTful endpoints for different functionalities
- **Error Handling**: Centralized exception handling and user-friendly responses
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

#### 2. Request/Response Models

- **ProcessRequest**: Pydantic model for incoming support requests
- **ProcessResponse**: Structured response with answer, sources, trace, and metrics
- **HealthResponse**: Health check status with timestamp and version info

#### 3. Integration Layer

- **Agent Workflow**: Seamless integration with LangGraph multi-agent pipeline
- **State Management**: Proper request lifecycle and state handling
- **Async Processing**: Non-blocking request processing for scalability

### API Endpoints

#### `GET /` - Root Endpoint

Returns basic API information and available endpoints.

**Response:**

```json
{
  "message": "Agentic Support Copilot API",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health` - Health Check

Monitors system health and service availability.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2023-12-01T10:30:00.000Z",
  "version": "0.1.0"
}
```

#### `POST /process` - Support Request Processing

Main endpoint for processing support requests through the multi-agent pipeline.

**Request:**

```json
{
  "request_text": "I forgot my password and need help resetting it"
}
```

**Response:**

```json
{
  "answer": "I understand you're having trouble with your password. Here's how to reset it...",
  "sources": [
    {
      "id": "doc1",
      "title": "Password Reset Guide",
      "content": "To reset your password, click the 'Forgot Password' link...",
      "similarity_score": 0.85
    }
  ],
  "trace": [
    {
      "agent_name": "ClassifierAgent",
      "step_name": "classify_request",
      "input": { "request_text": "I forgot my password..." },
      "output": {
        "intent": "account_issue",
        "sentiment": "neutral",
        "urgency": "high"
      },
      "duration_ms": 245,
      "timestamp": "2023-12-01T10:30:00.000Z"
    }
  ],
  "metrics": {
    "latency_ms": 1250,
    "token_usage": 450
  }
}
```

### Middleware Configuration

#### CORS Middleware

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error Handling Strategy

#### Input Validation

- Empty request text detection
- Request schema validation using Pydantic
- Malformed JSON handling

#### Pipeline Error Handling

- HTTPException propagation for validation errors
- Generic exception handling for system errors
- User-friendly error messages
- Detailed error logging for debugging

#### Response Format

```json
{
  "detail": "Request text cannot be empty"
}
```

## Setup Instructions

### Prerequisites

- Python 3.11+ installed
- Multi-agent pipeline implemented (Feature 003)
- OpenAI-compatible endpoint (Azure OpenAI or Azure AI Foundry) and Supabase credentials configured

### Environment Configuration

Ensure environment variables are set in the **root** `.env` file (same as Feature 003), then run `task setup-app` so they are copied into `apps/api/.env`:

```bash
# OpenAI-compatible endpoint from your Azure AI resource
OPENAI_ENDPOINT=https://your-foundry-project.openai.azure.com/
OPENAI_API_KEY=your-api-key

# Deployment names used by the backend (must match your Azure deployments)
OPENAI_DEPLOYMENT_NAME=gpt-4o
OPENAI_FAST_DEPLOYMENT_NAME=gpt-4o-mini
OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

### Installation and Running

```bash
cd apps/api

# Install dependencies
pip install -e ".[dev]"

# Run development server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Or run directly
python src/main.py
```

### Production Deployment

```bash
# Production server with workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (recommended for production)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API/Usage Examples

### Basic Request Processing

```python
import requests

# Process a support request
response = requests.post(
    "http://localhost:8000/process",
    json={"request_text": "I need help with my billing"}
)

if response.status_code == 200:
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"Sources used: {len(result['sources'])}")
    print(f"Processing time: {result['metrics']['latency_ms']}ms")
else:
    print(f"Error: {response.json()['detail']}")
```

### Health Monitoring

```python
import requests

# Check API health
response = requests.get("http://localhost:8000/health")
health_data = response.json()

if health_data["status"] == "healthy":
    print("API is running normally")
else:
    print("API has issues")
```

### Interactive Documentation

Access interactive API documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Frontend Integration Example

```javascript
// React/Frontend integration
const processSupportRequest = async (requestText) => {
  try {
    const response = await fetch("http://localhost:8000/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ request_text: requestText }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error processing request:", error);
    throw error;
  }
};
```

## Testing

### Running Unit Tests

```bash
cd apps/api
python -m pytest tests/test_api.py -v -p pytest_asyncio
```

### Test Coverage

The test suite covers:

- **Health Endpoint**: Status checking and response validation
- **Root Endpoint**: API information and metadata
- **Process Endpoint**: Request validation, workflow integration, error handling
- **CORS Configuration**: Cross-origin request handling
- **Request/Response Models**: Schema validation and structure
- **Integration Scenarios**: Concurrent requests, large payloads

### Manual Testing

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Process request
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"request_text": "I need help with my account"}'

# Test error handling
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"request_text": ""}'
```

### Load Testing

```bash
# Using Apache Bench for load testing
ab -n 100 -c 10 -p test_payload.json -T application/json \
  http://localhost:8000/process
```

## Troubleshooting

### Common Issues

#### 1. Server Startup Failures

**Problem**: `ModuleNotFoundError` or import errors
**Solutions**:

- Verify Python path and module structure
- Check all dependencies are installed
- Ensure environment variables are set
- Run from correct directory (`apps/api/`)

#### 2. CORS Errors in Frontend

**Problem**: Browser blocks cross-origin requests
**Solutions**:

- Verify CORS middleware configuration
- Check frontend URL matches allowed origins
- Ensure proper preflight request handling
- Test with browser developer tools

#### 3. Request Validation Errors

**Problem**: 422 validation errors for valid-looking requests
**Solutions**:

- Check JSON formatting and syntax
- Verify required fields are present
- Ensure content-type header is `application/json`
- Review Pydantic model definitions

#### 4. Pipeline Integration Issues

**Problem**: 500 errors during request processing
**Solutions**:

- Check agent pipeline implementation (Feature 003)
- Verify Azure OpenAI credentials and connectivity
- Examine error logs for specific failure points
- Test individual components separately

#### 5. Performance Issues

**Problem**: Slow response times or timeouts
**Solutions**:

- Monitor agent trace for bottlenecks
- Check Azure OpenAI rate limits and quotas
- Optimize knowledge base search queries
- Consider async optimization and caching

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python -m uvicorn src.main:app --reload
```

### Monitoring and Logging

```python
# Add custom logging in production
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Performance Considerations

### Optimization Strategies

- **Async Processing**: All endpoints use async/await patterns
- **Connection Pooling**: Reuse HTTP connections for external services
- **Request Validation**: Early validation to prevent unnecessary processing
- **Error Caching**: Cache frequent error responses
- **Rate Limiting**: Implement client-side rate limiting for API protection

### Scaling Recommendations

- **Horizontal Scaling**: Deploy multiple instances behind load balancer
- **Worker Processes**: Use multiple worker processes for CPU-bound tasks
- **Database Optimization**: Connection pooling and query optimization
- **Caching Layer**: Redis for frequent responses and session data
- **Monitoring**: Implement comprehensive metrics and alerting

### Resource Management

- **Memory Usage**: Monitor agent state and trace memory consumption
- **Token Limits**: Track Azure OpenAI token usage and implement limits
- **Connection Limits**: Configure appropriate connection pool sizes
- **Timeout Settings**: Set appropriate timeouts for external service calls

## Security Considerations

### Input Validation

- **Request Size Limits**: Prevent excessively large requests
- **Content Validation**: Sanitize and validate all input data
- **Rate Limiting**: Implement client rate limiting
- **Malicious Input**: Detect and block potential injection attempts

### Authentication & Authorization

- **API Keys**: Implement API key authentication for production
- **JWT Tokens**: Consider JWT for user authentication
- **Role-Based Access**: Implement role-based access control
- **Audit Logging**: Log all API requests for security monitoring

### Data Protection

- **PII Detection**: Avoid logging sensitive customer information
- **Data Encryption**: Use HTTPS for all API communications
- **Privacy Compliance**: Ensure compliance with privacy regulations
- **Data Retention**: Implement appropriate data retention policies

This API backend provides a robust, scalable foundation for the Agentic Support Copilot with comprehensive error handling, security features, and production-ready capabilities.
