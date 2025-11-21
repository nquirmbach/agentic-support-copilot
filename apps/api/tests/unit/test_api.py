#!/usr/bin/env python3
"""
Unit tests for FastAPI backend endpoints.

This test suite validates:
1. Health check endpoint
2. Root endpoint functionality
3. Process endpoint request/response handling
4. Error handling and validation
5. CORS middleware configuration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_workflow_result():
    """Mock result from AgentWorkflow."""
    return {
        "answer": "Here's how to reset your password...",
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
                "input": {"request_text": "I forgot my password"},
                "output": {"intent": "account_issue", "sentiment": "neutral", "urgency": "high"},
                "duration_ms": 245,
                "timestamp": "2023-12-01T10:30:00.000Z"
            }
        ],
        "metrics": {
            "latency_ms": 1250,
            "token_usage": 450
        }
    }


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self, client):
        """Test health endpoint returns successful response."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint_success(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Agentic Support Copilot API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestProcessEndpoint:
    """Test process endpoint functionality."""

    @patch('src.main.workflow')
    def test_process_request_success(self, mock_workflow, client, mock_workflow_result):
        """Test successful processing of a support request."""
        # Mock the workflow to return test data
        mock_workflow.process_request = AsyncMock(
            return_value=mock_workflow_result)

        # Send test request
        response = client.post(
            "/process",
            json={"request_text": "I forgot my password and need help resetting it"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == mock_workflow_result["answer"]
        assert len(data["sources"]) == 1
        assert data["sources"][0]["title"] == "Password Reset Guide"
        assert len(data["trace"]) == 1
        assert data["metrics"]["latency_ms"] == 1250

        # Verify workflow was called correctly
        mock_workflow.process_request.assert_called_once_with(
            "I forgot my password and need help resetting it"
        )

    def test_process_request_empty_text(self, client):
        """Test process endpoint rejects empty request text."""
        response = client.post("/process", json={"request_text": ""})

        assert response.status_code == 400
        data = response.json()
        assert "Request text cannot be empty" in data["detail"]

    def test_process_request_whitespace_only(self, client):
        """Test process endpoint rejects whitespace-only text."""
        response = client.post("/process", json={"request_text": "   \n\t   "})

        assert response.status_code == 400
        data = response.json()
        assert "Request text cannot be empty" in data["detail"]

    def test_process_request_missing_field(self, client):
        """Test process endpoint rejects missing request_text field."""
        response = client.post("/process", json={})

        assert response.status_code == 422  # Validation error

    @patch('src.main.workflow')
    def test_process_request_workflow_error(self, mock_workflow, client):
        """Test process endpoint handles workflow errors gracefully."""
        # Mock workflow to raise an exception
        mock_workflow.process_request = AsyncMock(
            side_effect=Exception("Test error"))

        response = client.post(
            "/process",
            json={"request_text": "This will cause an error"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "An error occurred while processing your request" in data["detail"]


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in responses."""
        response = client.get(
            "/health", headers={"Origin": "http://localhost:3000"})

        # Check for CORS headers - only origin header is added to simple requests
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_preflight_request(self, client):
        """Test CORS preflight request handling."""
        response = client.options(
            "/process",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


class TestRequestResponseModels:
    """Test request and response model validation."""

    def test_process_request_model_validation(self, client):
        """Test ProcessRequest model validation."""
        # Test with invalid data type
        response = client.post("/process", json={"request_text": 123})

        assert response.status_code == 422  # Validation error

    def test_process_response_structure(self, client, mock_workflow_result):
        """Test ProcessResponse model structure validation."""
        with patch('src.main.workflow') as mock_workflow:
            mock_workflow.process_request = AsyncMock(
                return_value=mock_workflow_result)

            response = client.post(
                "/process",
                json={"request_text": "Test request"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify required fields are present
            assert "answer" in data
            assert "sources" in data
            assert "trace" in data
            assert "metrics" in data

            # Verify metrics structure
            assert "latency_ms" in data["metrics"]
            assert "token_usage" in data["metrics"]

            # Verify source structure
            if data["sources"]:
                source = data["sources"][0]
                assert "id" in source
                assert "title" in source
                assert "content" in source
                assert "similarity_score" in source

            # Verify trace structure
            if data["trace"]:
                step = data["trace"][0]
                assert "agent_name" in step
                assert "step_name" in step
                assert "input" in step
                assert "output" in step
                assert "duration_ms" in step
                assert "timestamp" in step


class TestAPIIntegration:
    """Test API integration scenarios."""

    @patch('src.main.workflow')
    def test_multiple_concurrent_requests(self, mock_workflow, client, mock_workflow_result):
        """Test handling multiple concurrent requests."""
        import asyncio
        import concurrent.futures

        mock_workflow.process_request = AsyncMock(
            return_value=mock_workflow_result)

        def make_request():
            return client.post(
                "/process",
                json={"request_text": "Concurrent test request"}
            )

        # Send multiple requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

        # Verify workflow was called for each request
        assert mock_workflow.process_request.call_count == 5

    def test_large_request_handling(self, client):
        """Test handling of large request texts."""
        large_text = "This is a very long request. " * 1000  # ~20,000 characters

        with patch('src.main.workflow') as mock_workflow:
            mock_workflow.process_request = AsyncMock(return_value={
                "answer": "Response to large request",
                "sources": [],
                "trace": [],
                "metrics": {"latency_ms": 1000, "token_usage": 100}
            })

            response = client.post(
                "/process", json={"request_text": large_text})

            assert response.status_code == 200
            mock_workflow.process_request.assert_called_once_with(large_text)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
