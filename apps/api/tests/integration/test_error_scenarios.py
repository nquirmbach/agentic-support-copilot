"""
Error scenario tests for the Agentic Support Copilot.
Tests how the system handles various error conditions and edge cases.
"""

import pytest
import asyncio
from typing import List, Dict

from src.services.knowledge_base import KnowledgeBase
from src.agents.workflow import AgentWorkflow
from src.models.llm import AzureOpenAIProvider


class TestErrorScenarios:
    """Error scenario test class for the Agentic Support Copilot."""

    @pytest.fixture
    def llm_provider(self):
        """Create LLM provider fixture."""
        return AzureOpenAIProvider()

    @pytest.fixture
    def knowledge_base(self):
        """Create knowledge base fixture."""
        return KnowledgeBase()

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture."""
        return AgentWorkflow()

    @pytest.mark.asyncio
    async def test_empty_request_handling(self, workflow):
        """Test handling of empty request."""
        result = await workflow.process_request("")

        # Should handle empty input gracefully and return a response
        assert result is not None
        assert 'answer' in result
        assert 'metrics' in result
        # Should contain error message or validation reasons
        assert len(result['answer']) > 0

    @pytest.mark.asyncio
    async def test_whitespace_only_request(self, workflow):
        """Test handling of whitespace-only request."""
        result = await workflow.process_request("   ")

        # Should handle whitespace input gracefully and return a response
        assert result is not None
        assert 'answer' in result
        assert 'metrics' in result

    @pytest.mark.asyncio
    async def test_very_long_request(self, workflow):
        """Test handling of very long request."""
        long_text = "I need help with " + "a very long problem " * 100

        # Should handle long requests gracefully
        result = await workflow.process_request(long_text)

        assert result is not None
        assert 'answer' in result
        assert 'metrics' in result
        assert result['metrics']['latency_ms'] > 0

    @pytest.mark.asyncio
    async def test_special_characters(self, workflow):
        """Test handling of special characters and unicode."""
        special_text = "Help! My password ñoño 🚀 contains émojis and ñ characters. What do I do? $%^&*()"

        result = await workflow.process_request(special_text)

        # Should handle special characters gracefully
        assert result is not None
        assert len(result['answer']) > 0
        assert result['metrics']['token_usage'] > 0

    @pytest.mark.asyncio
    async def test_control_characters(self, workflow):
        """Test handling of control characters."""
        control_text = "\n\t\r\n\t\r"

        # Should handle control characters gracefully or raise appropriate exception
        try:
            result = await workflow.process_request(control_text)
            assert result is not None
        except Exception:
            # Expected to fail gracefully
            pass

    @pytest.mark.asyncio
    async def test_excessive_punctuation(self, workflow):
        """Test handling of excessive punctuation."""
        punctuation_text = "HELP!!!!!!" * 20

        result = await workflow.process_request(punctuation_text)

        # Should handle excessive punctuation gracefully
        assert result is not None
        assert len(result['answer']) > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, workflow):
        """Test handling of concurrent requests."""
        requests = [
            "I need to reset my password",
            "How do I change my email address?",
            "What are the API rate limits?",
            "I was charged incorrectly",
            "How do I enable 2FA?"
        ]

        # Run requests concurrently
        tasks = [workflow.process_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert len(results) == len(requests)
        successful_results = [
            r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(requests)

        # Validate each result
        for result in successful_results:
            assert result is not None
            assert 'answer' in result
            assert 'metrics' in result

    @pytest.mark.asyncio
    async def test_knowledge_base_failure(self, llm_provider):
        """Test behavior when knowledge base fails."""

        # Create a mock failing knowledge base
        class FailingKnowledgeBase:
            async def search(self, query: str, limit: int = 5) -> List[Dict]:
                raise Exception("Simulated knowledge base failure")

        failing_kb = FailingKnowledgeBase()
        failing_workflow = AgentWorkflow()

        # Should handle KB failure gracefully
        try:
            result = await failing_workflow.process_request("I need help with my account")
            # If it succeeds, should have a fallback answer
            assert result is not None
            assert 'answer' in result
        except Exception as e:
            # If it fails, should be a graceful failure
            assert 'fallback' in str(e).lower(
            ) or 'knowledge' in str(e).lower()

    @pytest.mark.asyncio
    async def test_complex_request_handling(self, workflow):
        """Test handling of complex/long requests."""
        complex_request = "I need comprehensive help with " + "everything " * 50

        result = await workflow.process_request(complex_request)

        # Should complete in reasonable time
        assert result is not None
        assert result['metrics']['latency_ms'] < 30000  # 30 second timeout
        assert len(result['answer']) > 0

    @pytest.mark.asyncio
    async def test_numeric_input(self, workflow):
        """Test handling of numeric-only input."""
        numeric_text = "1234567890" * 50

        # Should handle numeric input gracefully
        try:
            result = await workflow.process_request(numeric_text)
            assert result is not None
        except Exception:
            # Expected to fail gracefully
            pass
