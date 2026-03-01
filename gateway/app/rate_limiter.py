"""Rate limiting middleware for API Gateway."""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiter:
    """Token bucket rate limiter with configurable limits per user/role."""
    
    def __init__(self):
        self._buckets: Dict[str, Tuple[int, int]] = {}  # (tokens, last_update)
        self._limits: Dict[str, Dict] = defaultdict(lambda: {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000,
        })
        self._request_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "minute": 0,
            "hour": 0,
            "day": 0,
            "minute_start": time.time(),
            "hour_start": time.time(),
            "day_start": time.time(),
        })
    
    def set_limit(self, key: str, rpm: int = 60, rph: int = 1000, rpd: int = 10000):
        """Set rate limit for a specific key (user_id, role, or IP)."""
        self._limits[key] = {
            "requests_per_minute": rpm,
            "requests_per_hour": rph,
            "requests_per_day": rpd,
        }
    
    def check_limit(self, key: str) -> Tuple[bool, Dict]:
        """Check if request is within rate limit. Returns (allowed, info)."""
        current_time = time.time()
        counts = self._request_counts[key]
        limits = self._limits.get(key, self._limits["default"])
        
        elapsed_minute = current_time - counts["minute_start"]
        elapsed_hour = current_time - counts["hour_start"]
        elapsed_day = current_time - counts["day_start"]
        
        if elapsed_minute >= 60:
            counts["minute"] = 0
            counts["minute_start"] = current_time
        
        if elapsed_hour >= 3600:
            counts["hour"] = 0
            counts["hour_start"] = current_time
        
        if elapsed_day >= 86400:
            counts["day"] = 0
            counts["day_start"] = current_time
        
        allowed = (
            counts["minute"] < limits["requests_per_minute"] and
            counts["hour"] < limits["requests_per_hour"] and
            counts["day"] < limits["requests_per_day"]
        )
        
        info = {
            "remaining_minute": max(0, limits["requests_per_minute"] - counts["minute"]),
            "remaining_hour": max(0, limits["requests_per_hour"] - counts["hour"]),
            "remaining_day": max(0, limits["requests_per_day"] - counts["day"]),
            "limit_minute": limits["requests_per_minute"],
            "limit_hour": limits["requests_per_hour"],
            "limit_day": limits["requests_per_day"],
            "reset_at": counts["minute_start"] + 60,
        }
        
        if allowed:
            counts["minute"] += 1
            counts["hour"] += 1
            counts["day"] += 1
        
        return allowed, info
    
    def get_limits(self, key: str) -> Dict:
        """Get current limits for a key."""
        return self._limits.get(key, self._limits["default"])
    
    def get_usage(self, key: str) -> Dict:
        """Get current usage for a key."""
        counts = self._request_counts[key]
        limits = self._limits.get(key, self._limits["default"])
        return {
            "requests_this_minute": counts["minute"],
            "requests_this_hour": counts["hour"],
            "requests_this_day": counts["day"],
            "limits": limits,
        }


rate_limiter = RateLimiter()


rate_limiter.set_limit("default", rpm=60, rph=1000, rpd=10000)
rate_limiter.set_limit("admin", rpm=300, rph=5000, rpd=50000)
rate_limiter.set_limit("premium", rpm=120, rph=2000, rpd=20000)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        user_id = request.headers.get("X-User-ID", "")
        user_role = request.headers.get("X-User-Role", "default")
        
        key = user_id or client_ip
        
        if user_role == "admin":
            key = f"admin:{client_ip}"
        elif user_role == "premium":
            key = f"premium:{client_ip}"
        
        allowed, info = rate_limiter.check_limit(key)
        
        request.state.rate_limit_info = info
        request.state.rate_limit_key = key
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "message": "Rate limit exceeded",
                        "code": "RATE_LIMIT_EXCEEDED",
                        "details": info,
                    },
                },
                headers={
                    "X-RateLimit-Limit-Minute": str(info["limit_minute"]),
                    "X-RateLimit-Limit-Hour": str(info["limit_hour"]),
                    "X-RateLimit-Limit-Day": str(info["limit_day"]),
                    "X-RateLimit-Remaining-Minute": str(info["remaining_minute"]),
                    "X-RateLimit-Remaining-Hour": str(info["remaining_hour"]),
                    "X-RateLimit-Remaining-Day": str(info["remaining_day"]),
                    "X-RateLimit-Reset": str(int(info["reset_at"])),
                },
            )
        
        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit-Minute"] = str(info["limit_minute"])
        response.headers["X-RateLimit-Limit-Hour"] = str(info["limit_hour"])
        response.headers["X-RateLimit-Limit-Day"] = str(info["limit_day"])
        response.headers["X-RateLimit-Remaining-Minute"] = str(info["remaining_minute"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(info["remaining_hour"])
        response.headers["X-RateLimit-Remaining-Day"] = str(info["remaining_day"])
        
        return response
