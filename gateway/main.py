"""FastAPI gateway for aadhaar-chain identity platform."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings


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
