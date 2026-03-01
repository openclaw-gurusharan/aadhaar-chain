"""Routes for identity operations with agent integration."""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
import secrets
import hashlib

from app.models import (
    IdentityData,
    VerificationStatus,
    VerificationStep,
    AadhaarVerificationData,
    PanVerificationData,
    ApiResponse,
    SSOUser,
    SessionValidationResponse,
    TokenResponse,
    RefreshTokenRequest,
    ExternalTokenValidationRequest,
    ExternalTokenValidationResponse,
    UserRole,
    RoleAssignment,
    RoleAssignmentRequest,
    UserRolesResponse,
    UnifiedUserProfile,
    CreateUserRequest,
    UpdateUserRequest,
    UpdateUserRolesRequest,
    UserProfileResponse,
    Platform,
    KYCStatus,
)

from app.agent_manager import agent_manager
from gateway.config import settings


# In-memory stores (for development)
verifications: dict[str, VerificationStatus] = {}
identities: dict[str, IdentityData] = {}

# In-memory session store (for development)
sessions: dict[str, dict] = {}

# Refresh tokens store (token_hash -> {user_id, wallet_address, expires_at, rotated})
refresh_tokens: dict[str, dict] = {}

# User roles store (user_id -> list of RoleAssignment)
user_roles: dict[str, list[RoleAssignment]] = {}

# Unified user profiles store (user_id -> UnifiedUserProfile)
unified_users: dict[str, UnifiedUserProfile] = {}

# User profiles by wallet address (wallet_address -> user_id)
users_by_wallet: dict[str, str] = {}


router = APIRouter(prefix="/api/identity", tags=["identity"])

# Auth router
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

# User profile router
users_router = APIRouter(prefix="/api/users", tags=["users"])


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
    role: Optional[UserRole] = None
    platform: Optional[str] = "ondc_buyer"


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: SSOUser


def _generate_tokens(user: SSOUser, role: Optional[UserRole] = None, platform: Optional[str] = None) -> tuple[str, str]:
    """Generate access and refresh tokens with configurable audience/issuer."""
    now = datetime.utcnow()
    
    access_payload = {
        "sub": user.user_id,
        "wallet_address": user.wallet_address,
        "role": role.value if role else None,
        "platform": platform,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": now,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "type": "access",
    }
    
    access_token = jwt.encode(access_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    refresh_payload = {
        "sub": user.user_id,
        "wallet_address": user.wallet_address,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
        "iat": now,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "type": "refresh",
    }
    
    refresh_token = jwt.encode(refresh_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    refresh_tokens[refresh_token_hash] = {
        "user_id": user.user_id,
        "wallet_address": user.wallet_address,
        "expires_at": refresh_payload["exp"].isoformat() + "Z",
        "rotated": False,
    }
    
    return access_token, refresh_token


@auth_router.post("/login", response_model=LoginResponse, tags=["auth"])
async def login(request: LoginRequest):
    """POST /api/auth/login - Authenticate user and create session with JWT."""
    user = SSOUser(
        user_id=f"user_{request.wallet_address[:8]}",
        wallet_address=request.wallet_address,
        email=request.email,
        created_at=_get_timestamp(),
        last_login=_get_timestamp(),
    )
    
    access_token, refresh_token = _generate_tokens(user, request.role, request.platform)
    
    sessions[access_token] = {
        "user": user.model_dump(),
        "role": request.role.value if request.role else None,
        "platform": request.platform,
        "expires_at": (datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)).isoformat() + "Z",
    }
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
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


@auth_router.post("/refresh", response_model=TokenResponse, tags=["auth"])
async def refresh_token(request: RefreshTokenRequest):
    """POST /api/auth/refresh - Refresh access token with rotation."""
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        refresh_token_hash = hashlib.sha256(request.refresh_token.encode()).hexdigest()
        
        if refresh_token_hash not in refresh_tokens:
            raise HTTPException(status_code=401, detail="Refresh token not found")
        
        token_data = refresh_tokens[refresh_token_hash]
        
        if token_data.get("rotated"):
            for hash_key, data in list(refresh_tokens.items()):
                if data["user_id"] == token_data["user_id"] and data.get("rotated"):
                    del refresh_tokens[hash_key]
            raise HTTPException(status_code=401, detail="Refresh token already used")
        
        refresh_tokens[refresh_token_hash]["rotated"] = True
        
        user = SSOUser(
            user_id=payload["sub"],
            wallet_address=payload["wallet_address"],
            created_at=_get_timestamp(),
            last_login=_get_timestamp(),
        )
        
        role = UserRole(payload["role"]) if payload.get("role") else None
        platform = payload.get("platform")
        
        access_token, new_refresh_token = _generate_tokens(user, role, platform)
        
        sessions[access_token] = {
            "user": user.model_dump(),
            "role": role.value if role else None,
            "platform": platform,
            "expires_at": (datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)).isoformat() + "Z",
        }
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@auth_router.get("/validate-external", response_model=ExternalTokenValidationResponse, tags=["auth"])
async def validate_external_token(
    token: str,
    platform: str = "external",
    expected_issuer: Optional[str] = None,
):
    """GET /api/auth/validate-external - Validate cross-platform tokens."""
    try:
        expected_issuer = expected_issuer or settings.jwt_issuer
        
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=[settings.jwt_audience, platform],
            issuer=expected_issuer,
        )
        
        return ExternalTokenValidationResponse(
            valid=True,
            user_id=payload.get("sub"),
            wallet_address=payload.get("wallet_address"),
            role=UserRole(payload["role"]) if payload.get("role") else None,
            platform=payload.get("platform", platform),
        )
        
    except jwt.ExpiredSignatureError:
        return ExternalTokenValidationResponse(
            valid=False,
            error="Token expired",
        )
    except jwt.InvalidTokenError as e:
        return ExternalTokenValidationResponse(
            valid=False,
            error=f"Invalid token: {str(e)}",
        )


@auth_router.post("/roles", response_model=ApiResponse, tags=["auth"])
async def assign_role(request: RoleAssignmentRequest, authorization: Optional[str] = Header(None)):
    """POST /api/auth/roles - Assign a role to a user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = request.user_id
    
    if user_id not in user_roles:
        user_roles[user_id] = []
    
    role_assignment = RoleAssignment(
        user_id=user_id,
        role=request.role,
        platform=request.platform,
        assigned_at=_get_timestamp(),
        assigned_by=sessions[token]["user"]["user_id"],
    )
    
    user_roles[user_id].append(role_assignment)
    
    return ApiResponse(
        success=True,
        message=f"Role {request.role.value} assigned to user {user_id}",
        data=role_assignment.model_dump(),
    )


@auth_router.get("/roles/{user_id}", response_model=UserRolesResponse, tags=["auth"])
async def get_user_roles(user_id: str, authorization: Optional[str] = Header(None)):
    """GET /api/auth/roles/{user_id} - Get user's roles."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    wallet_address = sessions[token]["user"]["wallet_address"]
    
    roles = user_roles.get(user_id, [])
    
    return UserRolesResponse(
        user_id=user_id,
        wallet_address=wallet_address,
        roles=roles,
    )


@auth_router.delete("/roles/{user_id}", response_model=ApiResponse, tags=["auth"])
async def remove_role(
    user_id: str,
    role: UserRole,
    platform: str = "ondc_buyer",
    authorization: Optional[str] = Header(None),
):
    """DELETE /api/auth/roles/{user_id} - Remove a role from a user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    if user_id not in user_roles:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_roles[user_id] = [
        r for r in user_roles[user_id]
        if not (r.role == role and r.platform == platform)
    ]
    
    return ApiResponse(
        success=True,
        message=f"Role {role.value} removed from user {user_id}",
    )


# --- Unified User Profile Routes ---


@users_router.get("", response_model=ApiResponse, tags=["users"])
async def list_users(
    wallet_address: Optional[str] = None,
    kyc_status: Optional[KYCStatus] = None,
    platform: Optional[Platform] = None,
):
    """GET /api/users - List all users with optional filtering."""
    users = list(unified_users.values())
    
    if wallet_address:
        users = [u for u in users if u.wallet_address == wallet_address]
    
    if kyc_status:
        users = [u for u in users if u.kyc_status == kyc_status]
    
    if platform:
        users = [u for u in users if platform in u.platforms]
    
    return ApiResponse(
        success=True,
        message=f"Found {len(users)} users",
        data={"users": [u.model_dump() for u in users], "count": len(users)},
    )


@users_router.post("", response_model=ApiResponse, tags=["users"])
async def create_user(request: CreateUserRequest):
    """POST /api/users - Create a new user profile."""
    if request.wallet_address in users_by_wallet:
        existing_user_id = users_by_wallet[request.wallet_address]
        return ApiResponse(
            success=False,
            message="User already exists",
            error={"code": "USER_EXISTS", "user_id": existing_user_id},
        )
    
    user_id = f"user_{len(unified_users) + 1:06d}"
    now = _get_timestamp()
    
    user = UnifiedUserProfile(
        user_id=user_id,
        wallet_address=request.wallet_address,
        email=request.email,
        phone=request.phone,
        display_name=request.display_name,
        roles=[],
        platforms=[Platform.aadhaar_chain],
        kyc_status=KYCStatus.unverified,
        created_at=now,
        updated_at=now,
    )
    
    unified_users[user_id] = user
    users_by_wallet[request.wallet_address] = user_id
    
    return ApiResponse(
        success=True,
        message="User created successfully",
        data=user.model_dump(),
    )


@users_router.get("/{user_id}", response_model=ApiResponse, tags=["users"])
async def get_user(user_id: str):
    """GET /api/users/{user_id} - Get user profile by ID."""
    if user_id not in unified_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ApiResponse(
        success=True,
        data=unified_users[user_id].model_dump(),
    )


@users_router.put("/{user_id}", response_model=ApiResponse, tags=["users"])
async def update_user(user_id: str, request: UpdateUserRequest):
    """PUT /api/users/{user_id} - Update user profile."""
    if user_id not in unified_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = unified_users[user_id]
    
    if request.email is not None:
        user.email = request.email
    if request.phone is not None:
        user.phone = request.phone
    if request.display_name is not None:
        user.display_name = request.display_name
    if request.roles is not None:
        user.roles = request.roles
    if request.platforms is not None:
        user.platforms = request.platforms
    
    user.updated_at = _get_timestamp()
    unified_users[user_id] = user
    
    return ApiResponse(
        success=True,
        message="User updated successfully",
        data=user.model_dump(),
    )


@users_router.delete("/{user_id}", response_model=ApiResponse, tags=["users"])
async def delete_user(user_id: str):
    """DELETE /api/users/{user_id} - Delete user profile."""
    if user_id not in unified_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = unified_users[user_id]
    del unified_users[user_id]
    del users_by_wallet[user.wallet_address]
    
    return ApiResponse(
        success=True,
        message="User deleted successfully",
    )


@users_router.put("/{user_id}/roles", response_model=ApiResponse, tags=["users"])
async def update_user_roles(user_id: str, request: UpdateUserRolesRequest):
    """PUT /api/users/{user_id}/roles - Update user roles for a specific platform."""
    if user_id not in unified_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = unified_users[user_id]
    
    user.roles = request.roles
    if request.platform not in user.platforms:
        user.platforms.append(request.platform)
    user.updated_at = _get_timestamp()
    unified_users[user_id] = user
    
    _propagate_kyc_to_platforms(user)
    
    return ApiResponse(
        success=True,
        message=f"Roles updated for user {user_id}",
        data=user.model_dump(),
    )


@users_router.put("/{user_id}/kyc", response_model=ApiResponse, tags=["users"])
async def update_kyc_status(
    user_id: str,
    kyc_status: KYCStatus,
    document_type: Optional[str] = None,
):
    """PUT /api/users/{user_id}/kyc - Update KYC status and propagate to all platforms."""
    if user_id not in unified_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = unified_users[user_id]
    
    user.kyc_status = kyc_status
    if kyc_status == KYCStatus.verified:
        user.kyc_verified_at = _get_timestamp()
    if document_type:
        user.kyc_document_type = document_type
    user.updated_at = _get_timestamp()
    unified_users[user_id] = user
    
    _propagate_kyc_to_platforms(user)
    
    return ApiResponse(
        success=True,
        message=f"KYC status updated to {kyc_status.value}",
        data=user.model_dump(),
    )


@users_router.get("/{user_id}/platforms", response_model=ApiResponse, tags=["users"])
async def get_user_platforms(user_id: str):
    """GET /api/users/{user_id}/platforms - Get user's platform access with KYC status."""
    if user_id not in unified_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = unified_users[user_id]
    
    platform_status = {}
    for platform in Platform:
        platform_status[platform.value] = {
            "active": platform in user.platforms,
            "kyc_required": platform != Platform.aadhaar_chain,
            "kyc_verified": user.kyc_status == KYCStatus.verified if platform != Platform.aadhaar_chain else True,
        }
    
    return ApiResponse(
        success=True,
        data={
            "user_id": user_id,
            "wallet_address": user.wallet_address,
            "kyc_status": user.kyc_status.value,
            "platforms": platform_status,
        },
    )


def _propagate_kyc_to_platforms(user: UnifiedUserProfile):
    """Propagate KYC status to role assignments for cross-platform access."""
    user_id = user.user_id
    
    if user.kyc_status == KYCStatus.verified:
        for platform in user.platforms:
            platform_str = platform.value if isinstance(platform, Platform) else platform
            
            if platform_str not in user_roles.get(user_id, []):
                if user_id not in user_roles:
                    user_roles[user_id] = []
                
                role = UserRole.buyer if "buyer" in platform_str else UserRole.seller
                role_assignment = RoleAssignment(
                    user_id=user_id,
                    role=role,
                    platform=platform_str,
                    assigned_at=_get_timestamp(),
                    assigned_by="system",
                )
                user_roles[user_id].append(role_assignment)
