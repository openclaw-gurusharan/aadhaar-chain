"""Pydantic models for SSO authentication endpoints."""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Request model for login."""
    wallet_address: str = Field(..., description="Solana wallet address")
    signature: Optional[str] = Field(None, description="Wallet signature for verification")
    email: Optional[str] = Field(None, description="Email for email-based login")


class SessionInfo(BaseModel):
    """Session information for response."""
    session_id: int
    created_at: int
    last_active: int
    expires_at: int
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class ConnectedAppInfo(BaseModel):
    """Connected app information for response."""
    app_name: str
    first_accessed: int
    last_accessed: int
    display_name: str = Field(..., description="Human-readable app name")


class UserResponse(BaseModel):
    """User data returned from validate/me endpoints."""
    wallet_address: str
    pda_address: Optional[str] = None
    owner_pubkey: Optional[str] = None
    created_at: int


class LoginResponse(BaseModel):
    """Response model for successful login."""
    user: UserResponse
    session: SessionInfo


class ValidateResponse(BaseModel):
    """Response model for session validation."""
    valid: bool
    user: Optional[UserResponse] = None


class ConnectedAppsResponse(BaseModel):
    """Response model for connected apps list."""
    apps: list[ConnectedAppInfo]


class SessionsResponse(BaseModel):
    """Response model for user sessions list."""
    sessions: list[SessionInfo]
