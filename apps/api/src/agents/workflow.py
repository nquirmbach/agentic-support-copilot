from datetime import datetime
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..models.state import AgentState
from ..agents.classifier import ClassifierAgent
from ..agents.retriever import RetrieverAgent
from ..agents.writer import WriterAgent
from ..agents.guard import GuardAgent
from ..agents.logger import LoggerAgent


class AgentWorkflow:
    """Orchestrates the multi-agent pipeline using LangGraph."""

    def __init__(self):
        self.classifier = ClassifierAgent()
        self.retriever = RetrieverAgent()
        self.writer = WriterAgent()
        self.guard = GuardAgent()
        self.logger = LoggerAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes for each agent
        workflow.add_node("classify", self.classifier.classify)
        workflow.add_node("retrieve", self.retriever.retrieve)
        workflow.add_node("write", self.writer.write_response)
        workflow.add_node("validate", self.guard.validate_response)
        workflow.add_node("log", self.logger.log_and_evaluate)

        # Define the flow
        workflow.set_entry_point("classify")

        # After classification, always retrieve
        workflow.add_edge("classify", "retrieve")

        # After retrieval, always write
        workflow.add_edge("retrieve", "write")

        # After writing, always validate
        workflow.add_edge("write", "validate")

        # After validation, always log and end
        workflow.add_edge("validate", "log")
        workflow.add_edge("log", END)

        return workflow.compile()

    def create_initial_state(self, request_text: str) -> AgentState:
        """Create the initial state for a new request."""
        return {
            "request_text": request_text,
            "intent": None,
            "sentiment": None,
            "urgency": None,
            "sources": [],
            "answer": None,
            "is_safe": None,
            "validation_reasons": None,
            "trace": [],
            "metrics": {
                "latency_ms": 0,
                "token_usage": 0
            },
            "start_time": datetime.now()
        }

    async def process_request(self, request_text: str) -> Dict[str, Any]:
        """Process a support request through the complete agent pipeline."""
        initial_state = self.create_initial_state(request_text)

        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)

            # Return the response in the expected format
            return {
                "answer": final_state.get("answer", "No response generated."),
                "sources": final_state.get("sources", []),
                "trace": final_state.get("trace", []),
                "metrics": final_state.get("metrics", {
                    "latency_ms": 0,
                    "token_usage": 0
                })
            }

        except Exception as e:
            # Return error response
            return {
                "answer": f"An error occurred while processing your request: {str(e)}",
                "sources": [],
                "trace": [{
                    "agent_name": "Workflow",
                    "step_name": "error",
                    "input": {"request_text": request_text},
                    "output": {"error": str(e)},
                    "duration_ms": 0,
                    "timestamp": datetime.now().isoformat()
                }],
                "metrics": {
                    "latency_ms": 0,
                    "token_usage": 0
                }
            }
