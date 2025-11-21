# Phase 0 - Feature 003: Multi-Agent Pipeline

## Feature Overview

This feature implements the core multi-agent pipeline that processes support requests through a sequence of specialized AI agents. The pipeline provides intelligent classification, knowledge retrieval, response generation, safety validation, and comprehensive logging with metrics collection.

The multi-agent architecture enables:

- **Modular Processing**: Each agent handles a specific aspect of the support request
- **Transparent Operations**: Full traceability of all agent decisions and actions
- **Safety & Compliance**: Built-in validation for harmful content and policy violations
- **Performance Monitoring**: Detailed metrics and timing information for optimization
- **Knowledge Integration**: RAG-based retrieval from the vector knowledge base

## Technical Implementation

### Architecture Components

#### 1. LLM Provider Abstraction (`src/models/llm.py`)

- **LlmProvider Protocol**: Abstract interface defining `embed()` and `chat()` methods
- **AzureOpenAIProvider**: Concrete implementation using Azure OpenAI services
- **Environment Configuration**: Secure credential management via environment variables
- **Error Handling**: Comprehensive exception handling with retry logic

```python
class LlmProvider(ABC):
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str
```

#### 2. Agent State Management (`src/models/state.py`)

- **AgentState TypedDict**: Shared state schema for pipeline data flow
- **AgentStep**: Individual trace step structure with timing and metadata
- **Source**: Knowledge source format with similarity scores
- **Metrics**: Performance metrics collection structure

#### 3. Classifier Agent (`src/agents/classifier.py`)

- **Intent Classification**: Technical issue, billing, general question, feature request, complaint, account issue
- **Sentiment Analysis**: Positive, neutral, negative emotional tone detection
- **Urgency Assessment**: High, medium, low priority classification
- **Structured Output**: JSON-formatted classification results with error handling

#### 4. Retriever Agent (`src/agents/retriever.py`)

- **Vector Search**: Integration with Supabase pgvector for semantic similarity
- **Relevance Filtering**: Configurable similarity threshold (default 0.7)
- **Top-K Selection**: Returns most relevant knowledge snippets with metadata
- **Fallback Handling**: Graceful degradation when knowledge base is unavailable

#### 5. Writer Agent (`src/agents/writer.py`)

- **Grounded Generation**: Response generation based on retrieved knowledge
- **Context Injection**: Seamlessly integrates knowledge sources into prompts
- **Tone Management**: Professional yet empathetic response style
- **Quality Assurance**: Comprehensive response generation with fallbacks

#### 6. Guard Agent (`src/agents/guard.py`)

- **Safety Validation**: Detects harmful content and inappropriate language
- **Hallucination Detection**: Identifies claims not supported by knowledge sources
- **Policy Compliance**: Ensures responses adhere to organizational guidelines
- **Quality Checks**: Validates completeness and clarity of generated responses

#### 7. Logger Agent (`src/agents/logger.py`)

- **Trace Collection**: Captures complete execution timeline of all agents
- **Performance Metrics**: Latency measurement and token usage estimation
- **Quality Evaluation**: Success criteria assessment and issue identification
- **Final Reporting**: Comprehensive execution summary with actionable insights

#### 8. LangGraph Orchestration (`src/agents/workflow.py`)

- **State Graph**: Defines agent execution flow and state transitions
- **Error Handling**: Robust error recovery and fallback mechanisms
- **Async Execution**: Non-blocking pipeline processing for scalability
- **Interface Abstraction**: Clean API for frontend integration

### Pipeline Flow

```
Request Input → Classifier → Retriever → Writer → Guard → Logger → Response Output
     ↓              ↓           ↓        ↓       ↓        ↓
  State Init   Classification  KB Search  Response  Validation  Metrics
```

## Setup Instructions

### Prerequisites

- Python 3.11+ installed
- Azure AI resource (Azure OpenAI or Azure AI Foundry) deployed and configured (see Feature 000)
- Supabase project configured (see Feature 002)

### Environment Configuration

Create or update the **root** `.env` file (and then run `task setup-app` to copy it into `apps/api/.env`):

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

### Installation

```bash
cd apps/api
pip install -e ".[dev]"
```

## API/Usage Examples

### Direct Agent Usage

```python
from src.agents.workflow import AgentWorkflow

# Initialize workflow
workflow = AgentWorkflow()

# Process a support request
result = await workflow.process_request(
    "I can't log in to my account and need help resetting my password"
)

# Access results
answer = result["answer"]
sources = result["sources"]
trace = result["trace"]
metrics = result["metrics"]
```

### Individual Agent Usage

```python
from src.agents.classifier import ClassifierAgent
from src.models.state import AgentState

# Initialize classifier
classifier = ClassifierAgent()

# Create initial state
state = {
    "request_text": "My billing is wrong",
    "intent": None,
    "sentiment": None,
    "urgency": None,
    "sources": [],
    "answer": None,
    "is_safe": None,
    "validation_reasons": None,
    "trace": [],
    "metrics": {"latency_ms": 0, "token_usage": 0},
    "start_time": datetime.now()
}

# Classify request
classified_state = await classifier.classify(state)
print(f"Intent: {classified_state['intent']}")
print(f"Sentiment: {classified_state['sentiment']}")
print(f"Urgency: {classified_state['urgency']}")
```

### Response Format

```python
{
    "answer": "I understand you're having trouble logging in. Here's how to reset your password...",
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
            "input": {"request_text": "I can't log in..."},
            "output": {"intent": "account_issue", "sentiment": "negative", "urgency": "high"},
            "duration_ms": 245,
            "timestamp": "2023-12-01T10:30:00.000Z"
        }
        # ... additional trace steps
    ],
    "metrics": {
        "latency_ms": 1250,
        "token_usage": 450
    }
}
```

## Testing

### Running Unit Tests

```bash
cd apps/api
python -m pytest tests/test_agents.py -v -p pytest_asyncio
```

### Test Coverage

The test suite covers:

- **LLM Provider**: Interface compliance and mock functionality
- **Classifier Agent**: Classification accuracy and error handling
- **Retriever Agent**: Knowledge base integration and search functionality
- **Writer Agent**: Response generation and context injection
- **Guard Agent**: Safety validation and compliance checking
- **Logger Agent**: Metrics calculation and trace collection

### Integration Testing

```bash
# Test complete pipeline with real services
python scripts/test_knowledge_base.py

# Test API endpoint
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"request_text": "I need help with my account"}'
```

### Mock Testing

The test suite uses comprehensive mocking to test agent logic without requiring actual LLM calls:

```python
class MockLLMProvider(LlmProvider):
    async def embed(self, texts):
        return [[0.1] * 1536 for _ in texts]

    async def chat(self, messages):
        # Return appropriate mock responses based on context
        return json.dumps({"intent": "technical_issue", "sentiment": "neutral", "urgency": "medium"})
```

## Troubleshooting

### Common Issues

#### 1. Azure OpenAI Connection Errors

**Problem**: `Embedding generation failed` or `Chat completion failed`
**Solutions**:

- Verify API key and endpoint in environment variables
- Check deployment names match your Azure OpenAI resources
- Ensure proper network connectivity to Azure services
- Validate API version compatibility

#### 2. Classification Failures

**Problem**: Classifier returns default values instead of intelligent classification
**Solutions**:

- Check LLM provider is properly initialized
- Verify JSON parsing in classifier response handling
- Review system prompt for clarity and completeness
- Test with different input formats

#### 3. Knowledge Base Retrieval Issues

**Problem**: No sources returned or empty results from retriever
**Solutions**:

- Confirm Supabase connection and credentials
- Verify pgvector extension is enabled
- Check document embeddings are properly generated
- Adjust similarity threshold if too restrictive
- Validate knowledge base contains relevant documents

#### 4. Guard Agent False Positives

**Problem**: Valid responses marked as unsafe
**Solutions**:

- Review guard agent system prompt for clarity
- Adjust confidence thresholds in validation logic
- Examine knowledge source relevance to response
- Consider policy compliance requirements

#### 5. Performance Issues

**Problem**: Slow response times or high latency
**Solutions**:

- Monitor agent trace for bottlenecks
- Optimize LLM model selection and parameters
- Implement caching for repeated queries
- Consider async optimization opportunities
- Review knowledge base search efficiency

### Debug Mode

Enable detailed logging by setting environment variable:

```bash
export LOG_LEVEL=DEBUG
```

### Health Checks

Monitor system health with built-in endpoints:

```bash
curl http://localhost:8000/health
```

## Performance Considerations

### Optimization Strategies

- **Async Processing**: All agents implement async/await for non-blocking execution
- **Connection Pooling**: Reuse database and API connections where possible
- **Caching**: Consider Redis for frequently accessed knowledge and classifications
- **Batch Processing**: Process multiple requests concurrently when possible
- **Model Selection**: Choose appropriate Azure OpenAI models for cost/quality balance

### Scaling Recommendations

- **Horizontal Scaling**: Deploy multiple API instances behind load balancer
- **Resource Management**: Monitor Azure OpenAI rate limits and quota usage
- **Database Optimization**: Index Supabase tables for efficient vector operations
- **Monitoring**: Implement comprehensive logging and metrics collection

## Security Considerations

### Credential Management

- Store Azure OpenAI keys securely in environment variables
- Use Azure Key Vault for production credential management
- Implement proper API key rotation policies
- Monitor for unusual usage patterns

### Data Privacy

- Avoid logging sensitive customer information
- Implement data retention policies for traces and logs
- Ensure compliance with relevant privacy regulations
- Consider anonymization for analytics and monitoring

### Input Validation

- Sanitize all user inputs before processing
- Implement rate limiting to prevent abuse
- Add input size restrictions to prevent resource exhaustion
- Monitor for malicious prompt injection attempts

This multi-agent pipeline provides a robust, scalable foundation for intelligent customer support processing with comprehensive safety, monitoring, and quality assurance capabilities.
