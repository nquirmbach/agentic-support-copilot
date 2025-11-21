import time
from datetime import datetime
from typing import Dict, Any
from ..models.state import AgentState, AgentStep
from ..models.llm import get_llm_provider


class WriterAgent:
    """Agent for generating grounded responses based on retrieved knowledge."""

    def __init__(self):
        self.llm = get_llm_provider()

    async def write_response(self, state: AgentState) -> AgentState:
        """Generate a response based on the request and retrieved knowledge."""
        start_time = time.time()

        system_prompt = """You are a helpful customer support agent. Write a professional, empathetic response using the provided knowledge sources. Be concise, actionable, and address the customer's specific intent and urgency."""

        # Build context from sources
        sources_text = ""
        if state["sources"]:
            sources_text = "\n\nKnowledge Sources:\n"
            for i, source in enumerate(state["sources"], 1):
                sources_text += f"\n{i}. {source['title']}\n{source['content']}\n"
        else:
            sources_text = "\n\nNo specific knowledge sources were found for this request."

        user_prompt = f"""Customer Request:
{state['request_text']}

Classification:
- Intent: {state.get('intent', 'unknown')}
- Sentiment: {state.get('sentiment', 'unknown')}  
- Urgency: {state.get('urgency', 'unknown')}

{sources_text}

Please write a helpful response:"""

        try:
            response = await self.llm.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])

            # Create trace step
            step: AgentStep = {
                "agent_name": "WriterAgent",
                "step_name": "generate_response",
                "input": {
                    "request_text": state["request_text"],
                    "intent": state.get("intent"),
                    "sources_count": len(state["sources"])
                },
                "output": {
                    "response_length": len(response),
                    "response_preview": response[:200] + "..." if len(response) > 200 else response
                },
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }

            # Update state
            state["answer"] = response
            state["trace"].append(step)

            return state

        except Exception as e:
            # Add error step to trace
            error_step: AgentStep = {
                "agent_name": "WriterAgent",
                "step_name": "generate_response",
                "input": {
                    "request_text": state["request_text"],
                    "intent": state.get("intent"),
                    "sources_count": len(state["sources"])
                },
                "output": {"error": str(e)},
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }
            state["trace"].append(error_step)

            # Set fallback response
            state["answer"] = "I apologize, but I'm unable to generate a response at this moment. Please try again or contact our support team directly."

            return state
