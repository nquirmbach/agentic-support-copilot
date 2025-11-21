import asyncio
from datetime import datetime
from typing import Dict, Any, Callable, Awaitable
from langgraph.graph import StateGraph, END
from langgraph.types import RetryPolicy
from ..models.state import AgentState
from ..agents.classifier import ClassifierAgent
from ..agents.retriever import RetrieverAgent
from ..agents.writer import WriterAgent
from ..agents.guard import GuardAgent
from ..agents.logger import LoggerAgent
from ..config import (
    AGENT_MAX_RETRIES,
    AGENT_STEP_TIMEOUT_SECONDS,
)


class AgentWorkflow:
    """Orchestrates the multi-agent pipeline using LangGraph."""

    def __init__(self):
        self.classifier = ClassifierAgent()
        self.retriever = RetrieverAgent()
        self.writer = WriterAgent()
        self.guard = GuardAgent()
        self.logger = LoggerAgent()

        # Build and compile the workflow graph
        self.compiled_workflow = self._build_workflow()

    def _wrap_agent(
        self,
        agent_name: str,
        step_name: str,
        func: Callable[[AgentState], Awaitable[AgentState]],
    ) -> Callable[[AgentState], Awaitable[AgentState]]:
        async def wrapped(state: AgentState) -> AgentState:
            return await asyncio.wait_for(
                func(state), timeout=AGENT_STEP_TIMEOUT_SECONDS
            )

        return wrapped

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes for each agent with LangGraph retry policy and timeout handling
        retry_policy = RetryPolicy(max_attempts=AGENT_MAX_RETRIES)

        workflow.add_node(
            "classify",
            self._wrap_agent("ClassifierAgent", "classify",
                             self.classifier.classify),
            retry_policy=retry_policy,
        )
        workflow.add_node(
            "retrieve",
            self._wrap_agent("RetrieverAgent", "retrieve",
                             self.retriever.retrieve),
            retry_policy=retry_policy,
        )
        workflow.add_node(
            "write",
            self._wrap_agent("WriterAgent", "write",
                             self.writer.write_response),
            retry_policy=retry_policy,
        )
        workflow.add_node(
            "validate",
            self._wrap_agent("GuardAgent", "validate",
                             self.guard.validate_response),
            retry_policy=retry_policy,
        )
        workflow.add_node(
            "log",
            self._wrap_agent("LoggerAgent", "log",
                             self.logger.log_and_evaluate),
            retry_policy=retry_policy,
        )

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
        print("🔄 WORKFLOW: Starting process_request...")
        initial_state = self.create_initial_state(request_text)
        print("🔄 WORKFLOW: Initial state created, invoking workflow...")

        try:
            # Run the workflow
            final_state = await self.compiled_workflow.ainvoke(initial_state)
            print("🔄 WORKFLOW: Workflow completed successfully!")

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

    def visualize_workflow(self) -> str:
        """Generate a Mermaid diagram of the workflow."""
        try:
            # Get the graph from compiled workflow
            graph = self.compiled_workflow.get_graph()
            # Generate Mermaid diagram
            mermaid_diagram = graph.draw_mermaid()
            return mermaid_diagram
        except Exception as e:
            # Fallback to manual diagram if draw_mermaid fails
            return self._generate_manual_diagram()

    def _generate_manual_diagram(self) -> str:
        """Generate manual Mermaid diagram as fallback."""
        return """
```mermaid
graph TD
    A[Start: Request Text] --> B[Classifier Agent]
    B --> C[Retriever Agent]
    C --> D[Writer Agent]
    D --> E[Guard Agent]
    E --> F[Logger Agent]
    F --> G[End: Response]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#ffebee
    style F fill:#fce4ec
    style G fill:#e8f5e8
```
        """.strip()

    def save_workflow_diagram(self, filename: str = "workflow_diagram.md") -> str:
        """Save the workflow diagram to a file."""
        diagram = self.visualize_workflow()

        with open(filename, 'w') as f:
            f.write("# Agentic Support Copilot Workflow\n\n")
            f.write(
                "This diagram shows the sequential flow of agents processing support requests.\n\n")
            f.write(diagram)
            f.write("\n\n## Agent Descriptions\n\n")
            f.write(
                "1. **Classifier Agent**: Identifies intent, sentiment, and urgency\n")
            f.write(
                "2. **Retriever Agent**: Fetches relevant knowledge from the database\n")
            f.write("3. **Writer Agent**: Generates a grounded response\n")
            f.write("4. **Guard Agent**: Validates safety and compliance\n")
            f.write("5. **Logger Agent**: Logs metrics and final evaluation\n")

        return filename
