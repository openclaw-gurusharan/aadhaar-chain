"""Routes for identity operations with agent integration."""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt

from app.models import (
    IdentityData,
    VerificationStatus,
    VerificationStep,
    AadhaarVerificationData,
    PanVerificationData,
    ApiResponse,
    SSOUser,
    SessionValidationResponse,
)

from app.agent_manager import agent_manager
from gateway.config import settings


# In-memory stores (for development)
verifications: dict[str, VerificationStatus] = {}
identities: dict[str, IdentityData] = {}

# In-memory session store (for development)
sessions: dict[str, dict] = {}


router = APIRouter(prefix="/api/identity", tags=["identity"])

# Auth router
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


# --- Verification Routes with Agent Integration ---


@router.post("/{wallet_address}/aadhaar", response_model=ApiResponse, tags=["identity"])
async def create_aadhaar_verification(
    wallet_address: str,
    data: AadhaarVerificationData
):
    """Create Aadhaar card verification request and start agent workflow."""
    verification_id = await agent_manager.create_verification(
        wallet_address,
        "aadhaar",
        data
    )
    
    return ApiResponse(
        success=True,
        message=f"Aadhaar verification created: {verification_id}",
        data={
            "verification_id": verification_id,
            "status": "document_received"
        }
    )


@router.post("/{wallet_address}/pan", response_model=ApiResponse, tags=["identity"])
async def create_pan_verification(
    wallet_address: str,
    data: PanVerificationData
):
    """Create PAN card verification request and start agent workflow."""
    verification_id = await agent_manager.create_verification(
        wallet_address,
        "pan",
        data
    )
    
    return ApiResponse(
        success=True,
        message=f"PAN verification created: {verification_id}",
        data={
            "verification_id": verification_id,
            "status": "document_received"
        }
    )


@router.get("/status/{verification_id}", response_model=ApiResponse, tags=["identity"])
async def get_verification_status(
    verification_id: str,
):
    """Get verification status by ID."""
    status = await agent_manager.get_verification_status(verification_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return ApiResponse(
        success=True,
        data=status.model_dump()
    )


# --- Document Verification Routes with Agent Orchestration ---


@router.post("/verify/aadhaar", response_model=ApiResponse, tags=["identity"])
async def verify_aadhaar_document(
    wallet_address: str,
    document_data: bytes,  # Base64 encoded document data
    verification_data: Optional[dict] = None,
):
    """Verify Aadhaar card document using agent workflow."""
    
    # Create verification request
    verification_id = await agent_manager.create_verification(
        wallet_address,
        "aadhaar",
        verification_data
    )
    
    # Orchestrate verification workflow through agents
    status = await agent_manager.orchestrate_verification(
        wallet_address,
        "aadhaar",
        document_data,
        verification_data
    )
    
    return ApiResponse(
        success=True,
        message=f"Aadhaar verification {status.current_step.value}",
        data={
            "verification_id": verification_id,
            "status": status.current_step.value,
            "progress": status.progress,
            "decision": status.metadata.get("decision", "pending") if status.metadata else None,
        }
    )


@router.post("/verify/pan", response_model=ApiResponse, tags=["identity"])
async def verify_pan_document(
    wallet_address: str,
    document_data: bytes,  # Base64 encoded document data
    verification_data: Optional[dict] = None,
):
    """Verify PAN card document using agent workflow."""
    
    # Create verification request
    verification_id = await agent_manager.create_verification(
        wallet_address,
        "pan",
        verification_data
    )
    
    # Orchestrate verification workflow through agents
    status = await agent_manager.orchestrate_verification(
        wallet_address,
        "pan",
        document_data,
        verification_data
    )
    
    return ApiResponse(
        success=True,
        message=f"PAN verification {status.current_step.value}",
        data={
            "verification_id": verification_id,
            "status": status.current_step.value,
            "progress": status.progress,
            "decision": status.metadata.get("decision", "pending") if status.metadata else None,
        }
    )


# --- Identity Routes ---


@router.get("/{wallet_address}", response_model=ApiResponse, tags=["identity"])
async def get_identity(
    wallet_address: str,
):
    """Get identity data for wallet address."""
    if wallet_address not in identities:
        # Create new identity if not exists
        identities[wallet_address] = IdentityData(
            did=f"did:{wallet_address}",
            wallet_address=wallet_address,
            verification_bitmap=0,
            created_at=_get_timestamp(),
            updated_at=_get_timestamp(),
        )
    
    return ApiResponse(
        success=True,
        data=identities[wallet_address].model_dump()
    )


@router.post("/{wallet_address}", response_model=ApiResponse, tags=["identity"])
async def update_identity(
    wallet_address: str,
    data: dict,
):
    """Update identity data for wallet address."""
    if wallet_address not in identities:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    # Update identity (e.g., set verification bits)
    if "verification_bitmap" in data:
        identities[wallet_address].verification_bitmap = data["verification_bitmap"]
    
    identities[wallet_address].updated_at = _get_timestamp()
    
    return ApiResponse(
        success=True,
        message="Identity updated",
        data=identities[wallet_address].model_dump()
    )


# --- Helper Functions ---


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


# --- SSO Auth Routes ---


class LoginRequest(BaseModel):
    """Login request model."""
    wallet_address: str
    email: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: SSOUser


@auth_router.post("/login", response_model=LoginResponse, tags=["auth"])
async def login(request: LoginRequest):
    """POST /api/auth/login - Authenticate user and create session."""
    user = SSOUser(
        user_id=f"user_{request.wallet_address[:8]}",
        wallet_address=request.wallet_address,
        email=request.email,
        created_at=_get_timestamp(),
        last_login=_get_timestamp(),
    )
    
    payload = {
        "user_id": user.user_id,
        "wallet_address": user.wallet_address,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    
    sessions[token] = {
        "user": user.model_dump(),
        "expires_at": payload["exp"].isoformat() + "Z",
    }
    
    return LoginResponse(
        access_token=token,
        user=user,
    )


@auth_router.get("/validate", response_model=SessionValidationResponse, tags=["auth"])
async def validate_session(authorization: Optional[str] = Header(None)):
    """GET /api/auth/validate - Validate session token."""
    if not authorization or not authorization.startswith("Bearer "):
        return SessionValidationResponse(
            valid=False,
            error="Missing or invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    
    if token not in sessions:
        return SessionValidationResponse(
            valid=False,
            error="Invalid or expired session",
        )
    
    session_data = sessions[token]
    user = SSOUser(**session_data["user"])
    
    return SessionValidationResponse(
        valid=True,
        user=user,
        expires_at=session_data["expires_at"],
    )


@auth_router.get("/me", response_model=ApiResponse, tags=["auth"])
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    session_data = sessions[token]
    user = SSOUser(**session_data["user"])
    
    return ApiResponse(
        success=True,
        message="User retrieved",
        data=user.model_dump(),
    )


@auth_router.post("/logout", response_model=ApiResponse, tags=["auth"])
async def logout(authorization: Optional[str] = Header(None)):
    """Logout and invalidate session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        if token in sessions:
            del sessions[token]
    
    return ApiResponse(
        success=True,
        message="Logged out successfully",
    )
