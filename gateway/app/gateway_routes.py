"""Gateway routes for API Gateway functionality."""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional
import time
from datetime import datetime

from app.rate_limiter import rate_limiter
from app.models import ApiResponse


router = APIRouter(prefix="/api/gateway", tags=["gateway"])


class GatewayMetrics:
    """Track gateway metrics."""
    
    def __init__(self):
        self._requests_total = 0
        self._requests_by_service: Dict[str, int] = {}
        self._requests_by_status: Dict[str, int] = {}
        self._response_times: list = []
        self._start_time = time.time()
    
    def record_request(self, service: str, status: str, response_time: float):
        """Record a request."""
        self._requests_total += 1
        self._requests_by_service[service] = self._requests_by_service.get(service, 0) + 1
        self._requests_by_status[status] = self._requests_by_status.get(status, 0) + 1
        self._response_times.append(response_time)
        
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        avg_response_time = (
            sum(self._response_times) / len(self._response_times)
            if self._response_times else 0
        )
        
        return {
            "requests_total": self._requests_total,
            "requests_by_service": self._requests_by_service,
            "requests_by_status": self._requests_by_status,
            "average_response_time_ms": round(avg_response_time * 1000, 2),
            "uptime_seconds": int(time.time() - self._start_time),
        }
    
    def reset(self):
        """Reset metrics."""
        self._requests_total = 0
        self._requests_by_service = {}
        self._requests_by_status = {}
        self._response_times = []
        self._start_time = time.time()


gateway_metrics = GatewayMetrics()


SERVICE_ROUTES = {
    "identity": "/api/identity",
    "health": "/health",
    "docs": "/api/docs",
}


@router.get("/health", tags=["gateway"])
async def gateway_health() -> ApiResponse:
    """Gateway health check endpoint."""
    return ApiResponse(
        success=True,
        message="Gateway is healthy",
        data={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {
                "identity": "available",
                "routing": "active",
                "rate_limiting": "active",
            },
            "version": "1.0.0",
        },
    )


@router.get("/rate-limit", tags=["gateway"])
async def get_rate_limit_info(request: Request) -> ApiResponse:
    """Get rate limit information for the current user."""
    key = getattr(request.state, "rate_limit_key", "default")
    usage = rate_limiter.get_usage(key)
    limits = rate_limiter.get_limits(key)
    
    return ApiResponse(
        success=True,
        message="Rate limit info retrieved",
        data={
            "key": key,
            "usage": usage,
            "limits": limits,
            "tier": "default" if ":" not in key else key.split(":")[0],
        },
    )


@router.post("/rate-limit", tags=["gateway"])
async def set_rate_limit(
    key: str,
    rpm: Optional[int] = 60,
    rph: Optional[int] = 1000,
    rpd: Optional[int] = 10000,
) -> ApiResponse:
    """Set custom rate limit for a user or IP."""
    rate_limiter.set_limit(key, rpm=rpm, rph=rph, rpd=rpd)
    
    return ApiResponse(
        success=True,
        message=f"Rate limit updated for {key}",
        data={
            "key": key,
            "limits": rate_limiter.get_limits(key),
        },
    )


@router.get("/metrics", tags=["gateway"])
async def get_metrics() -> ApiResponse:
    """Get gateway metrics."""
    return ApiResponse(
        success=True,
        message="Metrics retrieved",
        data=gateway_metrics.get_metrics(),
    )


@router.post("/metrics/reset", tags=["gateway"])
async def reset_metrics() -> ApiResponse:
    """Reset gateway metrics."""
    gateway_metrics.reset()
    
    return ApiResponse(
        success=True,
        message="Metrics reset",
        data={"status": "reset"},
    )


@router.get("/routes", tags=["gateway"])
async def get_routes() -> ApiResponse:
    """Get available service routes."""
    return ApiResponse(
        success=True,
        message="Routes retrieved",
        data={
            "services": SERVICE_ROUTES,
            "gateway_prefix": "/api/gateway",
        },
    )


@router.post("/route/{service}", tags=["gateway"])
async def add_service_route(
    service: str,
    path: str,
) -> ApiResponse:
    """Add or update a service route."""
    SERVICE_ROUTES[service] = path
    
    return ApiResponse(
        success=True,
        message=f"Route added for {service}",
        data={
            "service": service,
            "path": path,
        },
    )


@router.get("/services", tags=["gateway"])
async def list_services() -> ApiResponse:
    """List all available services."""
    return ApiResponse(
        success=True,
        message="Services retrieved",
        data={
            "services": [
                {
                    "name": "identity",
                    "description": "Identity verification and management",
                    "endpoint": "/api/identity",
                    "status": "active",
                },
                {
                    "name": "health",
                    "description": "Health check service",
                    "endpoint": "/health",
                    "status": "active",
                },
                {
                    "name": "docs",
                    "description": "API documentation",
                    "endpoint": "/api/docs",
                    "status": "active",
                },
            ],
            "total_services": 3,
        },
    )


def record_gateway_request(service: str, status: str, response_time: float):
    """Record a gateway request for metrics."""
    gateway_metrics.record_request(service, status, response_time)
