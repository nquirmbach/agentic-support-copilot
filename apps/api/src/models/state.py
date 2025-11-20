from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class AgentStep(TypedDict):
    """Individual agent step in the trace."""
    agent_name: str
    step_name: str
    input: Any
    output: Any
    duration_ms: int
    timestamp: str


class Source(TypedDict):
    """Knowledge source retrieved by RAG."""
    id: str
    title: str
    content: str
    similarity_score: float


class Metrics(TypedDict):
    """Performance metrics."""
    latency_ms: int
    token_usage: int


class AgentState(TypedDict):
    """Shared state for the agent pipeline."""
    # Input
    request_text: str

    # Classification results
    intent: Optional[str]
    sentiment: Optional[str]
    urgency: Optional[str]

    # Retrieval results
    sources: List[Source]

    # Generated content
    answer: Optional[str]

    # Validation results
    is_safe: Optional[bool]
    validation_reasons: Optional[List[str]]

    # Trace and metrics
    trace: List[AgentStep]
    metrics: Metrics

    # Internal state
    start_time: datetime
