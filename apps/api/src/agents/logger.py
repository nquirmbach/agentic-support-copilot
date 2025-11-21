import time
from datetime import datetime
from typing import Dict, Any
from ..models.state import AgentState, AgentStep, Metrics


class LoggerAgent:
    """Agent for logging traces, calculating metrics, and final evaluation."""

    def __init__(self):
        pass

    async def log_and_evaluate(self, state: AgentState) -> AgentState:
        """Log the complete trace and calculate final metrics."""
        start_time = time.time()

        try:
            # Calculate final metrics
            total_latency = int(
                (datetime.now() - state["start_time"]).total_seconds() * 1000)

            # Estimate token usage based on trace
            estimated_tokens = self._estimate_token_usage(state)

            final_metrics: Metrics = {
                "latency_ms": total_latency,
                "token_usage": estimated_tokens
            }

            # Create final trace step
            final_step: AgentStep = {
                "agent_name": "LoggerAgent",
                "step_name": "final_evaluation",
                "input": {
                    "total_steps": len(state["trace"]),
                    "sources_used": len(state["sources"]),
                    "response_generated": bool(state.get("answer")),
                    "validation_passed": state.get("is_safe", False)
                },
                "output": {
                    "final_metrics": final_metrics,
                    "evaluation": self._generate_evaluation(state)
                },
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }

            # Update state
            state["trace"].append(final_step)
            state["metrics"] = final_metrics

            return state

        except Exception as e:
            # Add error step to trace
            error_step: AgentStep = {
                "agent_name": "LoggerAgent",
                "step_name": "final_evaluation",
                "input": {
                    "total_steps": len(state["trace"]),
                    "sources_used": len(state["sources"]),
                    "response_generated": bool(state.get("answer")),
                    "validation_passed": state.get("is_safe", False)
                },
                "output": {"error": str(e)},
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }
            state["trace"].append(error_step)

            # Set minimal metrics on error
            state["metrics"] = {
                "latency_ms": int((datetime.now() - state["start_time"]).total_seconds() * 1000),
                "token_usage": 0
            }

            return state

    def _estimate_token_usage(self, state: AgentState) -> int:
        """Estimate token usage based on trace and content."""
        # Rough estimation based on content length and agent steps
        base_tokens = 50  # Base tokens per agent step
        # Rough estimate: 1 token ≈ 4 chars
        request_tokens = len(state.get("request_text", "")) // 4
        response_tokens = len(state.get("answer", "")) // 4
        sources_tokens = sum(len(source.get("content", ""))
                             for source in state["sources"]) // 4

        estimated = (len(state["trace"]) * base_tokens) + \
            request_tokens + response_tokens + sources_tokens
        return max(estimated, 100)  # Minimum 100 tokens

    def _generate_evaluation(self, state: AgentState) -> Dict[str, Any]:
        """Generate a simple evaluation of the pipeline execution."""
        return {
            "success": bool(state.get("answer") and state.get("is_safe", False)),
            "agents_executed": len(state["trace"]),
            "sources_found": len(state["sources"]),
            "classification_completed": bool(state.get("intent")),
            "retrieval_completed": True,  # Always completes even if no sources
            "response_generated": bool(state.get("answer")),
            "validation_passed": state.get("is_safe", False),
            "issues": state.get("validation_reasons", []) if not state.get("is_safe", False) else []
        }
