# Phase 0 - Feature 006: Testing & Validation

## Feature Overview

This feature implements comprehensive testing and validation for the Agentic Support Copilot system. The testing framework ensures end-to-end functionality, validates the multi-agent pipeline execution, tests API endpoints, and verifies error handling across all system components.

The testing framework delivers:

- **Integration Testing**: Complete end-to-end validation of the multi-agent pipeline
- **API Endpoint Testing**: FastAPI endpoint validation and error handling
- **Error Scenario Testing**: Edge cases, failure modes, and graceful degradation
- **Performance Validation**: Latency, token usage, and system metrics verification
- **Quality Assessment**: Automated quality scoring and recommendations
- **Comprehensive Reporting**: Detailed test reports with actionable insights

## Technical Implementation

### Architecture Overview

#### 1. Test Suite Structure

```
apps/api/scripts/
├── test_integration.py      # End-to-end integration tests
├── test_error_scenarios.py  # Error handling and edge cases
├── test_api_endpoints.py    # API endpoint validation
└── run_all_tests.py         # Comprehensive test runner
```

#### 2. Testing Components

- **IntegrationTester**: Validates complete request flow through all agents
- **ErrorScenarioTester**: Tests system behavior under failure conditions
- **APIEndpointTester**: Validates HTTP endpoints and API contracts
- **ComprehensiveTestRunner**: Orchestrates all test suites and generates reports

### Test Categories

#### 1. Integration Tests (`test_integration.py`)

**Purpose**: Validate the complete end-to-end flow from request to response.

**Test Coverage**:

- **Request Classification**: Intent, sentiment, urgency detection
- **Knowledge Retrieval**: Vector search and source relevance
- **Response Generation**: Grounded answer creation
- **Safety Validation**: Guard agent compliance checking
- **Metrics Accuracy**: Latency and token usage tracking
- **Trace Completeness**: All agent steps properly logged

**Sample Test Cases**:

```python
test_cases = [
    ("Password Reset", "I need to reset my password, I forgot it", "password"),
    ("Login Issue", "I can't log into my account, it says invalid credentials", "login"),
    ("Billing Inquiry", "I was charged twice this month, can you help?", "billing"),
    ("Urgent Outage", "The system is down and I can't access my data", "urgent"),
    ("Security Concern", "I think someone accessed my account without permission", "security"),
]
```

**Validation Criteria**:

- Response structure completeness
- Agent pipeline execution order
- Knowledge source relevance
- Metrics accuracy (±100ms tolerance)
- Intent classification accuracy

#### 2. Error Scenario Tests (`test_error_scenarios.py`)

**Purpose**: Ensure graceful handling of edge cases and system failures.

**Test Coverage**:

- **Empty Requests**: Blank and whitespace-only inputs
- **Large Payloads**: Very long request handling
- **Special Characters**: Unicode, emojis, and special symbols
- **Malformed Input**: Control characters and excessive punctuation
- **Concurrent Requests**: Multiple simultaneous requests
- **Knowledge Base Failures**: Fallback behavior when KB is unavailable
- **LLM Timeouts**: Handling of slow model responses

**Error Handling Validation**:

```python
async def test_empty_request(self) -> Dict[str, Any]:
    """Test handling of empty request."""
    try:
        result = await self.workflow.process_request("")
        return {
            'success': True,
            'handled_gracefully': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'handled_gracefully': 'empty' in str(e).lower(),
            'error': str(e)
        }
```

**Graceful Degradation Targets**:

- System never crashes on invalid input
- Meaningful error messages provided
- Fallback responses available when components fail
- Concurrent request handling without resource exhaustion

#### 3. API Endpoint Tests (`test_api_endpoints.py`)

**Purpose**: Validate FastAPI endpoints, HTTP contracts, and CORS configuration.

**Test Coverage**:

- **Health Check**: `/health` endpoint functionality
- **Root Endpoint**: Basic server response
- **Process Endpoint**: Valid request handling and response structure
- **Input Validation**: Empty requests, missing fields, large payloads
- **CORS Headers**: Cross-origin request support
- **Concurrent Requests**: Multiple simultaneous API calls

**API Validation Examples**:

```python
def test_process_endpoint_valid(self) -> Dict[str, Any]:
    """Test the /process endpoint with valid input."""
    valid_request = {"request_text": "I need to reset my password"}

    response = self.session.post(f"{self.base_url}/process", json=valid_request)

    return {
        'success': response.status_code == 200,
        'has_required_fields': all(field in response.json() for field in ['answer', 'sources', 'trace', 'metrics']),
        'metrics_valid': all(field in response.json()['metrics'] for field in ['latency_ms', 'token_usage'])
    }
```

**API Contract Validation**:

- HTTP status codes correctness
- Response schema compliance
- CORS header presence and values
- Request validation and error responses
- Performance under concurrent load

#### 4. Comprehensive Test Runner (`run_all_tests.py`)

**Purpose**: Orchestrate all test suites and generate unified reports.

**Features**:

- **Test Orchestration**: Executes all test suites in sequence
- **Result Aggregation**: Combines results from all test categories
- **Quality Assessment**: Calculates overall system quality score
- **Performance Analysis**: Aggregates latency and token usage metrics
- **Report Generation**: Creates detailed JSON reports with recommendations
- **Error Tracking**: Identifies and categorizes system issues

**Quality Assessment Algorithm**:

```python
def assess_quality(self, detailed_results: Dict[str, Any]) -> Dict[str, Any]:
    score = 100
    issues = []

    # API quality (20 points)
    if api_success_rate < 95:
        score -= 20
        issues.append(f"API success rate below 95%: {api_success_rate}%")

    # Integration quality (25 points)
    if integration_success_rate < 90:
        score -= 25
        issues.append(f"Integration success rate below 90%: {integration_success_rate}%")

    # Performance quality (15 points)
    if avg_latency > 10000:  # 10 seconds
        score -= 15
        issues.append(f"Average response time too high: {avg_latency:.0f}ms")

    # Error handling quality (20 points)
    if error_success_rate < 80:
        score -= 20
        issues.append(f"Error handling success rate below 80%: {error_success_rate}%")

    return {
        'overall_score': max(0, score),
        'status': self.determine_status(score),
        'issues': issues
    }
```

### Performance Metrics and Targets

#### 1. Response Time Targets

- **Excellent**: < 2000ms average latency
- **Good**: 2000-5000ms average latency
- **Needs Improvement**: > 5000ms average latency

#### 2. Success Rate Targets

- **API Endpoints**: > 95% success rate
- **Integration Tests**: > 90% success rate
- **Error Handling**: > 80% graceful handling rate

#### 3. Quality Score Categories

- **Excellent (90-100)**: Ready for production deployment
- **Good (80-89)**: Minor issues, address before production
- **Fair (70-79)**: Significant improvements needed
- **Poor (< 70)**: Major issues, not production-ready

## Setup Instructions

### Prerequisites

- Python 3.11+ installed
- Backend API server running on localhost:8000
- OpenAI-compatible endpoint / Azure AI Foundry credentials configured
- Supabase connection configured (for knowledge base)

### Running Individual Test Suites

#### 1. API Endpoint Tests

```bash
cd apps/api/scripts
python test_api_endpoints.py
```

#### 2. Integration Tests

```bash
cd apps/api/scripts
python test_integration.py
```

#### 3. Error Scenario Tests

```bash
cd apps/api/scripts
python test_error_scenarios.py
```

### Running Comprehensive Test Suite

#### Complete Test Execution

```bash
cd apps/api/scripts
python run_all_tests.py
```

This will:

1. Execute all test suites in sequence
2. Generate comprehensive quality report
3. Save detailed results to `reports/test_report_YYYYMMDD_HHMMSS.json`
4. Provide overall system quality assessment

### Test Configuration

#### Environment Variables

```bash
# OpenAI-compatible endpoint (from Azure AI Foundry)
export OPENAI_ENDPOINT="your-endpoint"
export OPENAI_API_KEY="your-key"
export OPENAI_DEPLOYMENT_NAME="your-deployment"

# Supabase Configuration
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_KEY="your-supabase-service-role-key"
```

#### Custom Test Parameters

```python
# Modify test parameters in individual test files
API_BASE_URL = "http://localhost:8000"  # API endpoint
TIMEOUT_SECONDS = 30                    # Request timeout
MAX_CONCURRENT_REQUESTS = 5            # Concurrent test limit
```

## Usage Examples

### 1. Quick Health Check

```python
from scripts.test_api_endpoints import APIEndpointTester

tester = APIEndpointTester()
result = tester.test_health_endpoint()
print(f"Health check: {'✅' if result['success'] else '❌'}")
```

### 2. Integration Test Validation

```python
from scripts.test_integration import IntegrationTester

async def run_integration_test():
    tester = IntegrationTester()
    result = await tester.run_test_case(
        "Password Reset Test",
        "I need to reset my password",
        "password"
    )
    return result

# Run the test
result = asyncio.run(run_integration_test())
```

### 3. Error Scenario Testing

```python
from scripts.test_error_scenarios import ErrorScenarioTester

async def test_error_handling():
    tester = ErrorScenarioTester()
    results = await tester.test_empty_request()
    return results['handled_gracefully']

# Test error handling
graceful = asyncio.run(test_error_handling())
print(f"Error handling graceful: {'✅' if graceful else '❌'}")
```

### 4. Custom Test Case Creation

```python
# Add custom test cases to test_integration.py
custom_test_cases = [
    ("Custom Feature", "How do I use the new feature?", "feature"),
    ("Custom Issue", "The custom feature is broken", "bug"),
]

for test_name, request_text, expected_intent in custom_test_cases:
    result = await tester.run_test_case(test_name, request_text, expected_intent)
```

## Testing

### Manual Testing Procedures

#### 1. Pre-Test Setup

```bash
# Ensure API server is running
cd apps/api
python -m uvicorn src.main:app --reload

# Verify server health
curl http://localhost:8000/health
```

#### 2. Test Execution

```bash
# Run comprehensive test suite
cd apps/api/scripts
python run_all_tests.py

# Check results in generated report
cat reports/test_report_*.json | jq '.quality_assessment'
```

#### 3. Result Interpretation

- **Success Rate > 90%**: System is functioning well
- **Average Latency < 5000ms**: Performance is acceptable
- **Quality Score > 80**: Ready for production consideration

### Automated Testing Integration

#### CI/CD Pipeline Integration

```yaml
# Example GitHub Actions workflow
- name: Run Comprehensive Tests
  run: |
    cd apps/api/scripts
    python run_all_tests.py

- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: reports/
```

#### Scheduled Testing

```bash
# Run tests daily via cron
0 2 * * * cd /path/to/project && python apps/api/scripts/run_all_tests.py
```

## Troubleshooting

### Common Issues

#### 1. Server Connection Errors

**Problem**: `Cannot connect to server at localhost:8000`
**Solutions**:

- Ensure API server is running: `cd apps/api && python -m uvicorn src.main:app --reload`
- Check port availability: `lsof -i :8000`
- Verify firewall settings aren't blocking localhost connections

#### 2. Azure OpenAI Authentication

**Problem**: `Azure OpenAI authentication failed`
**Solutions**:

- Verify environment variables are set correctly
- Check API key validity and permissions
- Ensure deployment name matches Azure configuration
- Test connection manually: `curl -H "api-key: $AZURE_OPENAI_API_KEY" $AZURE_OPENAI_ENDPOINT`

#### 3. Supabase Connection Issues

**Problem**: `Supabase connection failed`
**Solutions**:

- Verify Supabase URL and API key
- Check network connectivity to Supabase
- Ensure vector extension is enabled: `CREATE EXTENSION IF NOT EXISTS vector;`
- Test connection manually via Supabase dashboard

#### 4. Test Timeouts

**Problem**: `Test script timed out after 5 minutes`
**Solutions**:

- Check system performance and available resources
- Increase timeout in test runner if needed
- Verify Azure OpenAI service availability
- Check for infinite loops in agent code

#### 5. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`
**Solutions**:

- Ensure running from correct directory: `cd apps/api/scripts`
- Check Python path includes project root
- Verify virtual environment is activated
- Install missing dependencies: `pip install -r requirements.txt`

### Debug Mode

#### Enable Verbose Logging

```python
# Add to test scripts for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed error traces
import traceback
try:
    result = await tester.run_test_case(...)
except Exception as e:
    print(f"Error details: {traceback.format_exc()}")
```

#### Individual Test Debugging

```bash
# Run specific test with debug output
python -c "
import asyncio
from test_integration import IntegrationTester
async def debug_test():
    tester = IntegrationTester()
    result = await tester.run_test_case('Debug Test', 'test request')
    print('Result:', result)
asyncio.run(debug_test())
"
```

### Performance Optimization

#### Test Execution Performance

- **Parallel Execution**: Use `asyncio.gather()` for concurrent test execution
- **Connection Pooling**: Reuse HTTP connections across API tests
- **Caching**: Cache knowledge base results for repeated test runs
- **Resource Management**: Properly clean up resources after each test

#### System Performance Monitoring

- **Memory Usage**: Monitor for memory leaks during test execution
- **CPU Utilization**: Track CPU usage during concurrent request tests
- **Network Latency**: Measure network overhead in API calls
- **Database Performance**: Monitor Supabase query performance

## Performance Considerations

### Test Execution Optimization

- **Selective Testing**: Run specific test suites based on changes
- **Parallel Execution**: Execute independent tests concurrently
- **Result Caching**: Cache expensive test results between runs
- **Incremental Testing**: Only run affected tests based on code changes

### Resource Management

- **Connection Limits**: Respect API rate limits during testing
- **Memory Efficiency**: Clean up large objects between test cases
- **Timeout Handling**: Implement appropriate timeouts for all operations
- **Error Recovery**: Ensure test suite can recover from individual test failures

### Scalability Testing

- **Load Testing**: Gradually increase concurrent request count
- **Stress Testing**: Test system limits with high request volumes
- **Endurance Testing**: Run extended tests to check for memory leaks
- **Resource Monitoring**: Track system resources during test execution

This comprehensive testing framework ensures the Agentic Support Copilot meets high quality standards and is ready for production deployment with confidence in its reliability, performance, and error handling capabilities.
