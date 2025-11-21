#!/usr/bin/env python3
"""
API endpoint testing for the Agentic Support Copilot.
Tests the FastAPI endpoints directly for proper validation and error handling.
"""

import asyncio
import json
import time
from typing import Dict, Any, List
import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor

# API Configuration
API_BASE_URL = "http://localhost:8000"


class APIEndpointTester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the health check endpoint."""
        print("🧪 Testing /health endpoint...")

        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'Health Endpoint',
                'success': success,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'has_required_fields': success and all(field in data for field in ['status', 'timestamp', 'version']),
                'data': data if success else None
            }
        except Exception as e:
            return {
                'test_name': 'Health Endpoint',
                'success': False,
                'error': str(e)
            }

    def test_root_endpoint(self) -> Dict[str, Any]:
        """Test the root endpoint."""
        print("🧪 Testing / endpoint...")

        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)

            return {
                'test_name': 'Root Endpoint',
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'content_type': response.headers.get('content-type', ''),
                'has_content': len(response.text) > 0
            }
        except Exception as e:
            return {
                'test_name': 'Root Endpoint',
                'success': False,
                'error': str(e)
            }

    def test_process_endpoint_valid(self) -> Dict[str, Any]:
        """Test the /process endpoint with valid input."""
        print("🧪 Testing /process endpoint with valid input...")

        valid_request = {
            "request_text": "I need to reset my password"
        }

        try:
            response = self.session.post(
                f"{self.base_url}/process",
                json=valid_request,
                timeout=30
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            # Validate response structure
            required_fields = ['answer', 'sources', 'trace', 'metrics']
            has_required_fields = success and all(
                field in data for field in required_fields)

            # Validate metrics
            metrics_valid = False
            if has_required_fields:
                metrics = data.get('metrics', {})
                metrics_valid = all(field in metrics for field in [
                                    'latency_ms', 'token_usage'])

            # Validate trace
            trace_valid = False
            if has_required_fields:
                trace = data.get('trace', [])
                trace_valid = len(trace) > 0 and all(
                    'agent_name' in step for step in trace)

            return {
                'test_name': 'Process Endpoint Valid',
                'success': success,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'has_required_fields': has_required_fields,
                'metrics_valid': metrics_valid,
                'trace_valid': trace_valid,
                'has_answer': bool(data.get('answer')) if success else False,
                'data': data if success else None
            }
        except Exception as e:
            return {
                'test_name': 'Process Endpoint Valid',
                'success': False,
                'error': str(e)
            }

    def test_process_endpoint_empty(self) -> Dict[str, Any]:
        """Test the /process endpoint with empty request."""
        print("🧪 Testing /process endpoint with empty request...")

        empty_request = {
            "request_text": ""
        }

        try:
            response = self.session.post(
                f"{self.base_url}/process",
                json=empty_request,
                timeout=10
            )

            # Should return 400 for empty request
            success = response.status_code == 400
            data = response.json() if response.headers.get(
                'content-type', '').startswith('application/json') else {}

            return {
                'test_name': 'Process Endpoint Empty',
                'success': success,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'returns_400': response.status_code == 400,
                'has_error_detail': 'detail' in data,
                'error_message': data.get('detail', '') if success else ''
            }
        except Exception as e:
            return {
                'test_name': 'Process Endpoint Empty',
                'success': False,
                'error': str(e)
            }

    def test_process_endpoint_missing_field(self) -> Dict[str, Any]:
        """Test the /process endpoint with missing required field."""
        print("🧪 Testing /process endpoint with missing field...")

        invalid_request = {
            "wrong_field": "some text"
        }

        try:
            response = self.session.post(
                f"{self.base_url}/process",
                json=invalid_request,
                timeout=10
            )

            # Should return 422 for validation error
            success = response.status_code == 422
            data = response.json() if response.headers.get(
                'content-type', '').startswith('application/json') else {}

            return {
                'test_name': 'Process Endpoint Missing Field',
                'success': success,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'returns_422': response.status_code == 422,
                'has_validation_error': 'detail' in data,
                'error_message': data.get('detail', '') if success else ''
            }
        except Exception as e:
            return {
                'test_name': 'Process Endpoint Missing Field',
                'success': False,
                'error': str(e)
            }

    def test_process_endpoint_large_payload(self) -> Dict[str, Any]:
        """Test the /process endpoint with large payload."""
        print("🧪 Testing /process endpoint with large payload...")

        large_text = "I need help with " + "a very detailed problem " * 200
        large_request = {
            "request_text": large_text
        }

        try:
            response = self.session.post(
                f"{self.base_url}/process",
                json=large_request,
                timeout=60
            )

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'Process Endpoint Large Payload',
                'success': success,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'handled_large_payload': success,
                'input_length': len(large_text),
                'has_answer': bool(data.get('answer')) if success else False
            }
        except Exception as e:
            return {
                'test_name': 'Process Endpoint Large Payload',
                'success': False,
                'error': str(e)
            }

    def test_cors_headers(self) -> Dict[str, Any]:
        """Test CORS headers are properly set."""
        print("🧪 Testing CORS headers...")

        try:
            # Test preflight request
            response = self.session.options(
                f"{self.base_url}/process",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=10
            )

            cors_headers = {
                'access_control_allow_origin': response.headers.get('access-control-allow-origin'),
                'access_control_allow_methods': response.headers.get('access-control-allow-methods'),
                'access_control_allow_headers': response.headers.get('access-control-allow-headers')
            }

            has_cors_headers = all(cors_headers.values())
            allows_frontend = cors_headers['access_control_allow_origin'] == 'http://localhost:3000'

            return {
                'test_name': 'CORS Headers',
                'success': has_cors_headers and allows_frontend,
                'status_code': response.status_code,
                'cors_headers': cors_headers,
                'has_cors_headers': has_cors_headers,
                'allows_frontend': allows_frontend
            }
        except Exception as e:
            return {
                'test_name': 'CORS Headers',
                'success': False,
                'error': str(e)
            }

    def test_concurrent_requests(self) -> Dict[str, Any]:
        """Test concurrent API requests."""
        print("🧪 Testing concurrent API requests...")

        requests_data = [
            {"request_text": "I need to reset my password"},
            {"request_text": "How do I change my email?"},
            {"request_text": "What are the API limits?"},
            {"request_text": "I was charged incorrectly"},
            {"request_text": "Enable two-factor authentication"}
        ]

        def make_request(request_data):
            try:
                response = self.session.post(
                    f"{self.base_url}/process",
                    json=request_data,
                    timeout=30
                )
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'response_time_ms': 30000  # Timeout
                }

        start_time = time.time()

        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, req)
                           for req in requests_data]
                results = [future.result() for future in futures]

            end_time = time.time()
            total_time = (end_time - start_time) * 1000

            successful_requests = sum(1 for r in results if r['success'])
            average_response_time = sum(r['response_time_ms']
                                        for r in results) / len(results)

            return {
                'test_name': 'Concurrent API Requests',
                'success': successful_requests == len(requests_data),
                'total_requests': len(requests_data),
                'successful_requests': successful_requests,
                'total_time_ms': total_time,
                'average_response_time_ms': average_response_time,
                'results': results
            }
        except Exception as e:
            return {
                'test_name': 'Concurrent API Requests',
                'success': False,
                'error': str(e)
            }

    def run_all_api_tests(self) -> Dict[str, Any]:
        """Run all API endpoint tests."""
        print("🚀 Starting API Endpoint Tests")
        print("=" * 50)

        # First check if server is running
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ Server is not responding correctly")
                return {'success': False, 'error': 'Server not healthy'}
        except Exception as e:
            print(f"❌ Cannot connect to server at {self.base_url}")
            print(f"   Error: {str(e)}")
            print(
                "   Make sure the API server is running: cd apps/api && python -m uvicorn src.main:app --reload")
            return {'success': False, 'error': f'Cannot connect to server: {str(e)}'}

        print("✅ Server is running, starting tests...")

        test_functions = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_process_endpoint_valid,
            self.test_process_endpoint_empty,
            self.test_process_endpoint_missing_field,
            self.test_process_endpoint_large_payload,
            self.test_cors_headers,
            self.test_concurrent_requests,
        ]

        results = []
        successful_tests = 0

        for test_func in test_functions:
            try:
                result = test_func()
                results.append(result)
                if result['success']:
                    successful_tests += 1
            except Exception as e:
                results.append({
                    'test_name': test_func.__name__,
                    'success': False,
                    'error': f"Test framework error: {str(e)}"
                })

        # Calculate summary
        success_rate = (successful_tests / len(results)) * 100

        summary = {
            'total_tests': len(results),
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'results': results
        }

        self.print_summary(summary)
        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print API test summary."""
        print("\n" + "=" * 50)
        print("🌐 API ENDPOINT TEST SUMMARY")
        print("=" * 50)
        print(
            f"✅ Success Rate: {summary['success_rate']:.1f}% ({summary['successful_tests']}/{summary['total_tests']})")

        # Print test results
        for result in summary['results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test_name']}")
            if not result['success']:
                print(f"      Error: {result.get('error', 'Unknown')}")

        print("\n🎯 API Quality Targets:")
        print(
            f"   Success Rate > 90%: {'✅' if summary['success_rate'] > 90 else '❌'}")
        print(
            f"   All Endpoints Working: {'✅' if summary['success_rate'] == 100 else '❌'}")


def main():
    """Main entry point for API endpoint testing."""
    tester = APIEndpointTester()
    return tester.run_all_api_tests()


if __name__ == "__main__":
    result = main()
    exit(0 if result['success_rate'] > 90 else 1)
