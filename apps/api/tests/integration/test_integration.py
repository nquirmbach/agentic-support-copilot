"""
Integration tests for the Agentic Support Copilot.
Tests the complete end-to-end flow from API request to agent response.
"""

import pytest
import asyncio
import time
from typing import Dict, Any

from src.services.knowledge_base import KnowledgeBase
from src.agents.workflow import AgentWorkflow
from src.models.llm import AzureOpenAIProvider


class TestIntegration:
    """Integration test class for the Agentic Support Copilot."""

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

    def validate_response_structure(self, response: Dict[str, Any]) -> Dict[str, bool]:
        """Validate the structure of a response."""
        validation = {
            'has_answer': bool(response.get('answer')),
            'has_sources': 'sources' in response,
            'has_trace': 'trace' in response,
            'has_metrics': 'metrics' in response,
            'trace_complete': False,
            'metrics_accurate': False
        }

        # Validate trace completeness
        trace = response.get('trace', [])
        expected_agents = ['ClassifierAgent', 'RetrieverAgent',
                           'WriterAgent', 'GuardAgent', 'LoggerAgent']
        actual_agents = [step.get('agent_name') for step in trace]
        validation['trace_complete'] = all(
            agent in actual_agents for agent in expected_agents)

        # Validate metrics
        metrics = response.get('metrics', {})
        validation['metrics_accurate'] = (
            'latency_ms' in metrics and
            'token_usage' in metrics and
            metrics['latency_ms'] > 0 and
            metrics['token_usage'] > 0
        )

        return validation

    @pytest.mark.asyncio
    async def test_password_reset_request(self, workflow):
        """Test password reset request processing."""
        request_text = "I need to reset my password, I forgot it"

        start_time = time.time()
        result = await workflow.process_request(request_text)
        end_time = time.time()

        # Basic assertions
        assert result is not None
        assert 'answer' in result
        assert 'sources' in result
        assert 'trace' in result
        assert 'metrics' in result

        # Validate structure
        validation = self.validate_response_structure(result)
        assert validation['has_answer']
        assert validation['has_sources']
        assert validation['has_trace']
        assert validation['has_metrics']
        assert validation['trace_complete']
        assert validation['metrics_accurate']

        # Performance assertions
        actual_latency = (end_time - start_time) * 1000
        assert actual_latency < 30000  # Should complete within 30 seconds
        assert result['metrics']['latency_ms'] > 0
        assert result['metrics']['token_usage'] > 0

    @pytest.mark.asyncio
    async def test_login_issue_request(self, workflow):
        """Test login issue request processing."""
        request_text = "I can't log into my account, it says invalid credentials"

        result = await workflow.process_request(request_text)

        # Basic assertions
        assert result is not None
        assert len(result['answer']) > 0
        assert isinstance(result['sources'], list)
        assert len(result['trace']) > 0

        # Check trace contains all expected agents
        agent_names = [step['agent_name'] for step in result['trace']]
        expected_agents = ['ClassifierAgent', 'RetrieverAgent',
                           'WriterAgent', 'GuardAgent', 'LoggerAgent']
        for agent in expected_agents:
            assert agent in agent_names

    @pytest.mark.asyncio
    async def test_billing_inquiry_request(self, workflow):
        """Test billing inquiry request processing."""
        request_text = "I was charged twice this month, can you help?"

        result = await workflow.process_request(request_text)

        # Validate response structure
        validation = self.validate_response_structure(result)
        assert validation['has_answer']
        assert validation['has_metrics']

        # Check classification in trace
        classification = result['trace'][0]['output'] if result['trace'] else {
        }
        assert 'intent' in classification
        assert 'sentiment' in classification
        assert 'urgency' in classification

    @pytest.mark.asyncio
    async def test_urgent_outage_request(self, workflow):
        """Test urgent outage request processing."""
        request_text = "The system is down and I can't access my data"

        result = await workflow.process_request(request_text)

        # Should be classified as urgent
        classification = result['trace'][0]['output'] if result['trace'] else {
        }
        assert classification.get('urgency') == 'high'

        # Should have safety validation
        assert result.get('is_safe') is not None

    @pytest.mark.asyncio
    async def test_feature_request(self, workflow):
        """Test feature request processing."""
        request_text = "How do I enable two-factor authentication?"

        result = await workflow.process_request(request_text)

        # Basic validation
        assert result is not None
        assert len(result['answer']) > 10  # Should have meaningful content
        assert result['metrics']['latency_ms'] > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, workflow):
        """Test handling of multiple concurrent requests."""
        requests = [
            "I need to reset my password",
            "How do I change my email address?",
            "What are the API rate limits?"
        ]

        # Run requests concurrently
        tasks = [workflow.process_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert len(results) == len(requests)
        for result in results:
            assert not isinstance(result, Exception)
            assert result is not None
            assert 'answer' in result

    @pytest.mark.asyncio
    async def test_empty_request_handling(self, workflow):
        """Test handling of empty request."""
        result = await workflow.process_request("")

        # Should handle empty input gracefully and return a response
        assert result is not None
        assert 'answer' in result
        assert 'metrics' in result
        # Should contain some response even for empty input
        assert len(result['answer']) > 0

    @pytest.mark.asyncio
    async def test_special_characters(self, workflow):
        """Test handling of special characters and unicode."""
        request_text = "Help! My password ñoño 🚀 contains émojis and ñ characters."

        result = await workflow.process_request(request_text)

        # Should handle special characters gracefully
        assert result is not None
        assert len(result['answer']) > 0
        assert result['metrics']['token_usage'] > 0
