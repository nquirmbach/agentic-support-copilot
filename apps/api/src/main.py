from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from datetime import datetime

from .agents.workflow import AgentWorkflow
from .models.state import Source, AgentStep, Metrics
from .logging_config import setup_logging, get_logger, set_request_id


class ProcessRequest(BaseModel):
    """Request model for processing support requests."""
    request_text: str


class ProcessResponse(BaseModel):
    """Response model for processed support requests."""
    answer: str
    sources: List[Source]
    trace: List[AgentStep]
    metrics: Metrics


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str


setup_logging()
logger = get_logger("api")


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Support Copilot API",
    description="Multi-agent support request processing system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow
workflow = AgentWorkflow()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0"
    )


@app.post("/process", response_model=ProcessResponse)
async def process_support_request(request: ProcessRequest):
    """Process a support request through the multi-agent pipeline."""
    request_id = set_request_id()
    logger.info("FASTAPI /process called", extra={"request_id": request_id})
    try:
        logger.info("FASTAPI validation started",
                    extra={"request_id": request_id})
        # Validate input
        if not request.request_text.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "EMPTY_REQUEST_TEXT",
                    "message": "Request text cannot be empty",
                },
            )
        logger.info("FASTAPI validation passed, invoking workflow",
                    extra={"request_id": request_id})

        # Process request through workflow
        result = await workflow.process_request(request.request_text)
        logger.info("FASTAPI workflow completed",
                    extra={"request_id": request_id})

        return ProcessResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        logger.exception("FASTAPI workflow error", extra={
                         "request_id": request_id})

        raise HTTPException(
            status_code=500,
            detail={
                "code": "WORKFLOW_ERROR",
                "message": "An error occurred while processing your request. Please try again.",
            },
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Agentic Support Copilot API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
