#!/usr/bin/env python3
"""
Unit tests for all agent implementations.

This test suite validates:
1. LLM Provider abstraction and Azure OpenAI implementation
2. Classifier Agent functionality
3. Retriever Agent functionality  
4. Writer Agent functionality
5. Guard Agent functionality
6. Logger Agent functionality
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.models.llm import LlmProvider, AzureOpenAIProvider, get_llm_provider
from src.models.state import AgentState, Source, AgentStep
from src.agents.classifier import ClassifierAgent
from src.agents.retriever import RetrieverAgent
from src.agents.writer import WriterAgent
from src.agents.guard import GuardAgent
from src.agents.logger import LoggerAgent


class MockLLMProvider(LlmProvider):
    """Mock LLM provider for testing."""

    def __init__(self):
        self.embed_calls = []
        self.chat_calls = []

    async def embed(self, texts):
        self.embed_calls.append(texts)
        # Return mock embeddings
        return [[0.1] * 1536 for _ in texts]

    async def chat(self, messages):
        self.chat_calls.append(messages)

        # Mock responses based on the last message content
        last_message = messages[-1]["content"] if messages else ""

        if "classify" in last_message.lower():
            return json.dumps({
                "intent": "technical_issue",
                "sentiment": "neutral",
                "urgency": "medium"
            })
        elif "validate" in last_message.lower():
            return json.dumps({
                "is_safe": True,
                "issues": [],
                "confidence": 0.9
            })
        else:
            return "This is a mock response for testing purposes."


@pytest.fixture
def mock_llm():
    """Fixture providing a mock LLM provider."""
    return MockLLMProvider()


@pytest.fixture
def sample_state():
    """Fixture providing a sample agent state."""
    return {
        "request_text": "I can't log in to my account",
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


class TestLLMProvider:
    """Test LLM Provider abstraction and implementation."""

    def test_get_llm_provider_returns_provider(self):
        """Test that factory function returns a valid LLM provider."""
        provider = get_llm_provider()
        assert isinstance(provider, LlmProvider)
        assert hasattr(provider, 'embed')
        assert hasattr(provider, 'chat')

    @pytest.mark.asyncio
    async def test_mock_llm_embed(self, mock_llm):
        """Test mock LLM embedding generation."""
        texts = ["test text 1", "test text 2"]
        embeddings = await mock_llm.embed(texts)

        assert len(embeddings) == 2
        assert len(embeddings[0]) == 1536
        assert mock_llm.embed_calls == [texts]

    @pytest.mark.asyncio
    async def test_mock_llm_chat(self, mock_llm):
        """Test mock LLM chat completion."""
        messages = [{"role": "user", "content": "test message"}]
        response = await mock_llm.chat(messages)

        assert isinstance(response, str)
        assert mock_llm.chat_calls == [messages]


class TestClassifierAgent:
    """Test Classifier Agent functionality."""

    @pytest.mark.asyncio
    async def test_classifier_with_mock_llm(self, sample_state, mock_llm):
        """Test classifier with mock LLM provider."""
        agent = ClassifierAgent()
        agent.llm = mock_llm  # Replace with mock

        result_state = await agent.classify(sample_state)

        # Check classification results
        assert result_state["intent"] == "technical_issue"
        assert result_state["sentiment"] == "neutral"
        assert result_state["urgency"] == "medium"

        # Check trace was updated
        assert len(result_state["trace"]) == 1
        step = result_state["trace"][0]
        assert step["agent_name"] == "ClassifierAgent"
        assert step["step_name"] == "classify_request"

    @pytest.mark.asyncio
    async def test_classifier_handles_json_error(self, sample_state, mock_llm):
        """Test classifier handles JSON parsing errors gracefully."""
        agent = ClassifierAgent()
        agent.llm = mock_llm
        # Make the mock return invalid JSON
        mock_llm.chat = AsyncMock(return_value="invalid json response")

        result_state = await agent.classify(sample_state)

        # Should fall back to default values
        assert result_state["intent"] == "general_question"
        assert result_state["sentiment"] == "neutral"
        assert result_state["urgency"] == "medium"


class TestRetrieverAgent:
    """Test Retriever Agent functionality."""

    @pytest.mark.asyncio
    async def test_retriever_with_mock_kb(self, sample_state):
        """Test retriever with mocked knowledge base."""
        agent = RetrieverAgent()

        # Mock the knowledge base
        mock_kb = AsyncMock()
        mock_kb.search_similar.return_value = [
            {
                "id": "doc1",
                "title": "Login Issues",
                "content": "Here's how to fix login problems...",
                "similarity": 0.85
            }
        ]
        agent.kb = mock_kb

        result_state = await agent.retrieve(sample_state)

        # Check retrieval results
        assert len(result_state["sources"]) == 1
        source = result_state["sources"][0]
        assert source["id"] == "doc1"
        assert source["title"] == "Login Issues"
        assert source["similarity_score"] == 0.85

        # Check trace was updated
        assert len(result_state["trace"]) == 1
        step = result_state["trace"][0]
        assert step["agent_name"] == "RetrieverAgent"

        # Verify KB was called correctly
        mock_kb.search_similar.assert_called_once_with(
            query=sample_state["request_text"],
            limit=5,
            threshold=0.7
        )


class TestWriterAgent:
    """Test Writer Agent functionality."""

    @pytest.mark.asyncio
    async def test_writer_with_mock_llm(self, sample_state, mock_llm):
        """Test writer with mock LLM provider."""
        # Set up state with sources
        sample_state["sources"] = [
            {
                "id": "doc1",
                "title": "Login Guide",
                "content": "Step 1: Enter your email...",
                "similarity_score": 0.85
            }
        ]

        agent = WriterAgent()
        agent.llm = mock_llm

        result_state = await agent.write_response(sample_state)

        # Check response was generated
        assert result_state["answer"] is not None
        assert isinstance(result_state["answer"], str)

        # Check trace was updated
        assert len(result_state["trace"]) == 1
        step = result_state["trace"][0]
        assert step["agent_name"] == "WriterAgent"
        assert step["step_name"] == "generate_response"


class TestGuardAgent:
    """Test Guard Agent functionality."""

    @pytest.mark.asyncio
    async def test_guard_with_mock_llm(self, sample_state, mock_llm):
        """Test guard with mock LLM provider."""
        # Set up state with answer
        sample_state["answer"] = "Here's how to fix your login issue..."
        sample_state["sources"] = []

        agent = GuardAgent()
        agent.llm = mock_llm

        result_state = await agent.validate_response(sample_state)

        # Check validation results
        assert result_state["is_safe"] is True
        assert result_state["validation_reasons"] == []

        # Check trace was updated
        assert len(result_state["trace"]) == 1
        step = result_state["trace"][0]
        assert step["agent_name"] == "GuardAgent"
        assert step["step_name"] == "validate_response"

    @pytest.mark.asyncio
    async def test_guard_handles_json_error(self, sample_state, mock_llm):
        """Test guard handles JSON parsing errors gracefully."""
        sample_state["answer"] = "Test response"
        agent = GuardAgent()
        agent.llm = mock_llm
        # Make the mock return invalid JSON
        mock_llm.chat = AsyncMock(return_value="invalid json response")

        result_state = await agent.validate_response(sample_state)

        # Should fall back to conservative validation
        assert result_state["is_safe"] is True
        assert "Unable to parse validation response" in result_state["validation_reasons"]


class TestLoggerAgent:
    """Test Logger Agent functionality."""

    @pytest.mark.asyncio
    async def test_logger_calculates_metrics(self, sample_state):
        """Test logger calculates metrics correctly."""
        # Set start_time to be in the past to ensure positive latency
        from datetime import timedelta
        sample_state["start_time"] = datetime.now() - timedelta(seconds=1)

        # Add some trace steps
        sample_state["trace"] = [
            {
                "agent_name": "TestAgent",
                "step_name": "test_step",
                "input": {},
                "output": {},
                "duration_ms": 100,
                "timestamp": datetime.now().isoformat()
            }
        ]
        sample_state["answer"] = "Test response"
        sample_state["is_safe"] = True

        agent = LoggerAgent()
        result_state = await agent.log_and_evaluate(sample_state)

        # Check metrics were calculated
        assert result_state["metrics"]["latency_ms"] > 0
        assert result_state["metrics"]["token_usage"] >= 100  # Minimum tokens

        # Check final trace step was added
        assert len(result_state["trace"]) == 2
        final_step = result_state["trace"][-1]
        assert final_step["agent_name"] == "LoggerAgent"
        assert final_step["step_name"] == "final_evaluation"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
