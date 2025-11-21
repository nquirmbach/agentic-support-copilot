import json
import time
from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from ..models.state import AgentState, AgentStep
from ..models.llm import get_llm_provider
from ..prompts import CLASSIFIER_SYSTEM_PROMPT
from ..logging_config import get_logger


class ClassifierAgent:
    """Agent for classifying support requests by intent, sentiment, and urgency."""

    def __init__(self):
        self.llm = get_llm_provider()
        self.logger = get_logger("classifier")

    async def classify(self, state: AgentState) -> AgentState:
        """Classify the support request."""
        self.logger.info("ClassifierAgent: starting classification")
        start_time = time.time()

        system_prompt = CLASSIFIER_SYSTEM_PROMPT

        user_prompt = f"Please classify this support request:\n\n{state['request_text']}"

        try:
            self.logger.info("ClassifierAgent: calling LLM (fast model)")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            self.logger.info(
                "ClassifierAgent: messages prepared",
            )

            response = await self.llm.chat(messages, fast=True)
            self.logger.info("ClassifierAgent: LLM response received")

            # Parse JSON response
            try:
                classification = json.loads(response)
            except json.JSONDecodeError:
                # Fallback classification if JSON parsing fails
                classification = {
                    "intent": "general_question",
                    "sentiment": "neutral",
                    "urgency": "medium"
                }

            # Create trace step
            step: AgentStep = {
                "agent_name": "ClassifierAgent",
                "step_name": "classify_request",
                "input": {"request_text": state["request_text"]},
                "output": classification,
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }

            # Update state
            state["intent"] = classification.get("intent", "general_question")
            state["sentiment"] = classification.get("sentiment", "neutral")
            state["urgency"] = classification.get("urgency", "medium")
            state["trace"].append(step)

            return state

        except Exception as e:
            # Add error step to trace
            error_step: AgentStep = {
                "agent_name": "ClassifierAgent",
                "step_name": "classify_request",
                "input": {"request_text": state["request_text"]},
                "output": {"error": str(e)},
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }
            state["trace"].append(error_step)

            # Set fallback values
            state["intent"] = "general_question"
            state["sentiment"] = "neutral"
            state["urgency"] = "medium"

            return state
