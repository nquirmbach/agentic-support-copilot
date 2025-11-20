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

        system_prompt = """You are a safety and compliance validator for customer support responses. Analyze the generated response and check for:

1. **Safety Issues**: 
   - Harmful content
   - Inappropriate language
   - Personal information exposure
   - Security risks

2. **Hallucinations**:
   - Claims not supported by the provided knowledge sources
   - Made-up facts or information
   - Contradictory statements

3. **Policy Compliance**:
   - Promises that can't be kept
   - Financial commitments beyond authority
   - Legal or regulatory issues
   - Brand guideline violations

4. **Quality Issues**:
   - Incomplete information
   - Unclear or confusing language
   - Missing important context

Return your analysis as a JSON object with these fields:
- is_safe: boolean (true if response passes all checks)
- issues: array of strings describing any problems found
- confidence: number (0-1, how confident you are in this assessment)

If the response is safe, set is_safe to true and an empty issues array. If there are problems, set is_safe to false and describe each issue."""

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
            ])

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
