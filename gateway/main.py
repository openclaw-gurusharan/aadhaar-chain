"""FastAPI gateway for aadhaar-chain identity platform."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from app.models import (
    AadhaarVerificationData,
    PanVerificationData,
    VerificationStatus,
    IdentityData,
    VerificationStep,
    ApiResponse,
)
from app.routes import router as identity_router
from app.agent_manager import agent_manager


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Gateway for identity & asset tokenization platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Include identity router
app.include_router(identity_router, prefix="/api")


# Startup event: Initialize agents
@app.on_event("startup")
async def startup_event():
    """Initialize Claude Agent SDK and agents on startup."""
    # TODO: Initialize Claude Agent SDK
    # TODO: Connect to MCP servers (document-processor, pattern-analyzer, compliance-rules)
    # TODO: Load agent definitions from mcp/agents.py
    # TODO: Initialize agent manager with configured agents
    pass


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> JSONResponse:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "status": "running",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
