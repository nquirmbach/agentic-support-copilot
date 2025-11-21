import json
import time
from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from ..models.state import AgentState, AgentStep
from ..models.llm import get_llm_provider


class ClassifierAgent:
    """Agent for classifying support requests by intent, sentiment, and urgency."""

    def __init__(self):
        self.llm = get_llm_provider()

    async def classify(self, state: AgentState) -> AgentState:
        """Classify the support request."""
        print("🏷️  CLASSIFIER AGENT: Starting classification...")
        start_time = time.time()

        system_prompt = """You are a support request classifier. Analyze the user's message and classify it into the following categories:

1. **Intent**: What type of support request is this?
   - "technical_issue" - Problems with software/hardware functionality
   - "billing_inquiry" - Questions about payments, subscriptions, refunds
   - "general_question" - General information requests
   - "feature_request" - Suggestions for new features
   - "complaint" - Expressions of dissatisfaction
   - "account_issue" - Problems with login, access, or account settings

2. **Sentiment**: What is the emotional tone?
   - "positive" - Happy, satisfied, pleased
   - "neutral" - Factual, informational, calm
   - "negative" - Angry, frustrated, disappointed

3. **Urgency**: How quickly does this need attention?
   - "high" - Critical issue, blocking functionality, urgent
   - "medium" - Important but not blocking, needs timely response
   - "low" - General inquiry, can wait for standard response

Return your response as a JSON object with these three fields."""

        user_prompt = f"Please classify this support request:\n\n{state['request_text']}"

        try:
            print("🤖 CLASSIFIER: Calling LLM chat (fast model)...")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            print(
                f"📝 CLASSIFIER: Messages prepared (system: {len(system_prompt)} chars, user: {len(user_prompt)} chars)")

            response = await self.llm.chat(messages, fast=True)
            print(f"✅ CLASSIFIER: LLM response received: {response[:100]}...")

            # Parse JSON response
            try:
                print("🔄 CLASSIFIER: Parsing JSON response...")
                classification = json.loads(response)
                print("✅ CLASSIFIER: JSON parsed successfully!")
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
