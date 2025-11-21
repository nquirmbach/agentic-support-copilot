import json
import time
from datetime import datetime
from typing import Dict, Any, List
from ..models.state import AgentState, AgentStep
from ..models.llm import get_llm_provider


class GuardAgent:
    """Agent for validating safety, hallucinations, and compliance."""

    def __init__(self):
        self.llm = get_llm_provider()

    async def validate_response(self, state: AgentState) -> AgentState:
        """Validate the generated response for safety and compliance."""
        start_time = time.time()

        system_prompt = """You are a safety validator for customer support responses. Check for harmful content, hallucinations, policy violations, and quality issues. Return JSON with: is_safe (boolean), issues (array of strings), confidence (0-1)."""

        user_prompt = f"""Original Request:
{state['request_text']}

Generated Response:
{state['answer']}

Available Knowledge Sources:
{json.dumps([{'title': s['title'], 'content': s['content']} for s in state['sources']], indent=2)}

Please validate this response:"""

        try:
            response = await self.llm.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], fast=True)

            # Parse JSON response
            try:
                validation = json.loads(response)
            except json.JSONDecodeError:
                # Fallback validation if JSON parsing fails
                validation = {
                    "is_safe": True,
                    "issues": ["Unable to parse validation response"],
                    "confidence": 0.5
                }

            # Create trace step
            step: AgentStep = {
                "agent_name": "GuardAgent",
                "step_name": "validate_response",
                "input": {
                    "request_text": state["request_text"],
                    "response_length": len(state.get("answer", "")),
                    "sources_count": len(state["sources"])
                },
                "output": validation,
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }

            # Update state
            state["is_safe"] = validation.get("is_safe", False)
            state["validation_reasons"] = validation.get("issues", [])
            state["trace"].append(step)

            return state

        except Exception as e:
            # Add error step to trace
            error_step: AgentStep = {
                "agent_name": "GuardAgent",
                "step_name": "validate_response",
                "input": {
                    "request_text": state["request_text"],
                    "response_length": len(state.get("answer", "")),
                    "sources_count": len(state["sources"])
                },
                "output": {"error": str(e)},
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }
            state["trace"].append(error_step)

            # Set conservative fallback values
            state["is_safe"] = False
            state["validation_reasons"] = [
                "Validation failed due to system error"]

            return state
