import time
from datetime import datetime
from typing import Dict, Any, List
from ..models.state import AgentState, AgentStep, Source
from ..services.knowledge_base import KnowledgeBase


class RetrieverAgent:
    """Agent for retrieving relevant knowledge from the knowledge base."""

    def __init__(self):
        self.kb = KnowledgeBase()

    async def retrieve(self, state: AgentState) -> AgentState:
        """Retrieve relevant knowledge based on the request."""
        start_time = time.time()

        try:
            # Search for relevant documents
            search_results = await self.kb.search_similar(
                query=state["request_text"],
                limit=5,
                threshold=0.7
            )

            # Convert to Source format
            sources: List[Source] = []
            for result in search_results:
                source: Source = {
                    "id": result["id"],
                    "title": result["title"],
                    "content": result["content"],
                    "similarity_score": result.get("similarity", 0.0)
                }
                sources.append(source)

            # Create trace step
            step: AgentStep = {
                "agent_name": "RetrieverAgent",
                "step_name": "retrieve_knowledge",
                "input": {
                    "request_text": state["request_text"],
                    "intent": state.get("intent")
                },
                "output": {
                    "sources_found": len(sources),
                    "sources": [{"id": s["id"], "title": s["title"], "score": s["similarity_score"]} for s in sources]
                },
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }

            # Update state
            state["sources"] = sources
            state["trace"].append(step)

            return state

        except Exception as e:
            # Add error step to trace
            error_step: AgentStep = {
                "agent_name": "RetrieverAgent",
                "step_name": "retrieve_knowledge",
                "input": {
                    "request_text": state["request_text"],
                    "intent": state.get("intent")
                },
                "output": {"error": str(e)},
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            }
            state["trace"].append(error_step)

            # Set empty sources on error
            state["sources"] = []

            return state
