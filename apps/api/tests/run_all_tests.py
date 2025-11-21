#!/usr/bin/env python3
"""
Comprehensive test runner for the Agentic Support Copilot.
Orchestrates all test suites and provides a complete validation report.
"""

import asyncio
import subprocess
import sys
import os
import time
from typing import Dict, Any, List
from datetime import datetime


class ComprehensiveTestRunner:
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}

    async def run_test_script(self, script_name: str, script_path: str) -> Dict[str, Any]:
        """Run a test script and capture its output."""
        print(f"\n{'='*60}")
        print(f"🚀 Running {script_name}")
        print(f"{'='*60}")

        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                'script_name': script_name,
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': time.time() - self.start_time
            }
        except subprocess.TimeoutExpired:
            return {
                'script_name': script_name,
                'success': False,
                'error': 'Test script timed out after 5 minutes',
                'execution_time': time.time() - self.start_time
            }
        except Exception as e:
            return {
                'script_name': script_name,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time
            }

    def parse_test_results(self, script_output: str) -> Dict[str, Any]:
        """Parse test results from script output."""
        try:
            # Look for JSON-like patterns in the output
            lines = script_output.split('\n')
            results = {}

            for line in lines:
                if 'Success Rate:' in line:
                    # Extract success rate percentage
                    import re
                    match = re.search(r'Success Rate: (\d+\.?\d*)%', line)
                    if match:
                        results['success_rate'] = float(match.group(1))

                if 'Average Latency:' in line:
                    # Extract average latency
                    import re
                    match = re.search(r'Average Latency: (\d+\.?\d*)ms', line)
                    if match:
                        results['average_latency_ms'] = float(match.group(1))

                if 'Average Tokens:' in line:
                    # Extract average tokens
                    import re
                    match = re.search(r'Average Tokens: (\d+\.?\d*)', line)
                    if match:
                        results['average_tokens'] = float(match.group(1))

            return results
        except Exception:
            return {}

    async def run_all_test_suites(self) -> Dict[str, Any]:
        """Run all test suites."""
        print("🧪 COMPREHENSIVE TEST SUITE FOR AGENTIC SUPPORT COPILOT")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Define test scripts to run
        test_scripts = [
            ("API Endpoint Tests", "integration/test_api_endpoints.py"),
            ("Integration Tests", "integration/test_integration.py"),
            ("Error Scenario Tests", "integration/test_error_scenarios.py"),
        ]

        script_dir = os.path.dirname(__file__)
        overall_success = True

        for script_name, script_file in test_scripts:
            script_path = os.path.join(script_dir, script_file)

            if not os.path.exists(script_path):
                print(f"❌ Test script not found: {script_path}")
                self.test_results[script_name] = {
                    'success': False,
                    'error': 'Script not found'
                }
                overall_success = False
                continue

            # Run the test script
            result = await self.run_test_script(script_name, script_path)
            self.test_results[script_name] = result

            # Print the output
            print(result['stdout'])
            if result['stderr']:
                print(f"STDERR: {result['stderr']}")

            if not result['success']:
                overall_success = False
                print(f"❌ {script_name} failed")
            else:
                print(f"✅ {script_name} completed successfully")

        # Generate comprehensive report
        end_time = time.time()
        total_execution_time = end_time - self.start_time

        report = self.generate_comprehensive_report(
            overall_success, total_execution_time)
        self.save_report_to_file(report)

        return report

    def generate_comprehensive_report(self, overall_success: bool, execution_time: float) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)

        # Calculate overall statistics
        total_suites = len(self.test_results)
        successful_suites = sum(
            1 for result in self.test_results.values() if result['success'])
        overall_success_rate = (
            successful_suites / total_suites) * 100 if total_suites > 0 else 0

        # Parse detailed results from each test suite
        detailed_results = {}
        for suite_name, result in self.test_results.items():
            if result['success'] and result['stdout']:
                detailed_results[suite_name] = self.parse_test_results(
                    result['stdout'])

        # Performance summary
        performance_summary = {}
        if 'Integration Tests' in detailed_results:
            perf = detailed_results['Integration Tests']
            performance_summary = {
                'average_latency_ms': perf.get('average_latency_ms', 0),
                'average_tokens': perf.get('average_tokens', 0),
                'integration_success_rate': perf.get('success_rate', 0)
            }

        # Quality assessment
        quality_assessment = self.assess_quality(detailed_results)

        report = {
            'timestamp': datetime.now().isoformat(),
            'execution_time_seconds': execution_time,
            'overall_success': overall_success,
            'summary': {
                'total_test_suites': total_suites,
                'successful_test_suites': successful_suites,
                'overall_success_rate': overall_success_rate
            },
            'test_suites': self.test_results,
            'detailed_results': detailed_results,
            'performance_summary': performance_summary,
            'quality_assessment': quality_assessment,
            'recommendations': self.generate_recommendations(quality_assessment, detailed_results)
        }

        # Print summary
        print(f"✅ Overall Success: {overall_success}")
        print(
            f"📊 Success Rate: {overall_success_rate:.1f}% ({successful_suites}/{total_suites})")
        print(f"⏱️  Total Execution Time: {execution_time:.1f} seconds")

        if performance_summary:
            print(
                f"🚀 Average Response Time: {performance_summary.get('average_latency_ms', 0):.0f}ms")
            print(
                f"🔢 Average Token Usage: {performance_summary.get('average_tokens', 0):.0f}")

        print(f"\n🎯 Quality Score: {quality_assessment['overall_score']}/100")
        print(f"📋 Status: {quality_assessment['status']}")

        # Print recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")

        return report

    def assess_quality(self, detailed_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the overall quality of the system."""
        score = 100
        issues = []

        # Check API tests
        if 'API Endpoint Tests' in detailed_results:
            api_success_rate = detailed_results['API Endpoint Tests'].get(
                'success_rate', 0)
            if api_success_rate < 95:
                score -= 20
                issues.append(
                    f"API success rate below 95%: {api_success_rate}%")

        # Check integration tests
        if 'Integration Tests' in detailed_results:
            integration_success_rate = detailed_results['Integration Tests'].get(
                'success_rate', 0)
            if integration_success_rate < 90:
                score -= 25
                issues.append(
                    f"Integration success rate below 90%: {integration_success_rate}%")

            avg_latency = detailed_results['Integration Tests'].get(
                'average_latency_ms', 0)
            if avg_latency > 10000:  # 10 seconds
                score -= 15
                issues.append(
                    f"Average response time too high: {avg_latency:.0f}ms")
            elif avg_latency > 5000:  # 5 seconds
                score -= 10
                issues.append(
                    f"Average response time elevated: {avg_latency:.0f}ms")

        # Check error handling
        if 'Error Scenario Tests' in detailed_results:
            error_success_rate = detailed_results['Error Scenario Tests'].get(
                'success_rate', 0)
            if error_success_rate < 80:
                score -= 20
                issues.append(
                    f"Error handling success rate below 80%: {error_success_rate}%")

        # Determine status
        if score >= 90:
            status = "Excellent - Ready for Production"
        elif score >= 80:
            status = "Good - Minor Issues"
        elif score >= 70:
            status = "Fair - Needs Improvements"
        else:
            status = "Poor - Significant Issues"

        return {
            'overall_score': max(0, score),
            'status': status,
            'issues': issues
        }

    def generate_recommendations(self, quality_assessment: Dict[str, Any], detailed_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if quality_assessment['overall_score'] < 90:
            recommendations.append(
                "Address failing tests before production deployment")

        # Performance recommendations
        if 'Integration Tests' in detailed_results:
            avg_latency = detailed_results['Integration Tests'].get(
                'average_latency_ms', 0)
            if avg_latency > 5000:
                recommendations.append(
                    "Optimize response times - consider caching or faster models")

            avg_tokens = detailed_results['Integration Tests'].get(
                'average_tokens', 0)
            if avg_tokens > 2000:
                recommendations.append(
                    "Optimize token usage - implement prompt optimization")

        # Error handling recommendations
        if 'Error Scenario Tests' in detailed_results:
            error_success_rate = detailed_results['Error Scenario Tests'].get(
                'success_rate', 0)
            if error_success_rate < 100:
                recommendations.append("Improve error handling for edge cases")

        # API recommendations
        if 'API Endpoint Tests' in detailed_results:
            api_success_rate = detailed_results['API Endpoint Tests'].get(
                'success_rate', 0)
            if api_success_rate < 100:
                recommendations.append(
                    "Fix API endpoint validation and error responses")

        if not recommendations:
            recommendations.append(
                "System is performing well - consider load testing for production readiness")

        return recommendations

    def save_report_to_file(self, report: Dict[str, Any]):
        """Save the test report to a file."""
        try:
            reports_dir = os.path.join(os.path.dirname(
                __file__), '..', '..', '..', 'reports')
            os.makedirs(reports_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(
                reports_dir, f"test_report_{timestamp}.json")

            with open(report_file, 'w') as f:
                import json
                json.dump(report, f, indent=2, default=str)

            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report to file: {str(e)}")


async def main():
    """Main entry point for comprehensive testing."""
    runner = ComprehensiveTestRunner()
    report = await runner.run_all_test_suites()

    # Exit with appropriate code
    if report['overall_success'] and report['quality_assessment']['overall_score'] >= 80:
        print("\n🎉 All tests completed successfully!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed or quality issues detected")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
