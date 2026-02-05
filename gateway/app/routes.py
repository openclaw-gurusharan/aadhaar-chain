"""Routes for identity operations with agent integration."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import time

from app.models import (
    IdentityData,
    VerificationStatus,
    VerificationStep,
    AadhaarVerificationData,
    PanVerificationData,
    ApiResponse,
    Credential,
    CredentialRequest,
)

from app.agent_manager import agent_manager


# In-memory stores (for development)
verifications: dict[str, VerificationStatus] = {}
identities: dict[str, IdentityData] = {}
credentials: dict[str, dict[str, Credential]] = {}  # wallet_address -> {credential_id: Credential}


router = APIRouter(prefix="/api/identity", tags=["identity"])


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
        message="Verification status retrieved",
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
            owner=wallet_address,
            commitment="",  # Empty commitment initially
            verification_bitmap=0,
            created_at=_get_timestamp(),
            updated_at=_get_timestamp(),
        )

    return ApiResponse(
        success=True,
        message="Identity retrieved",
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


@router.patch("/{wallet_address}", response_model=ApiResponse, tags=["identity"])
async def patch_identity(
    wallet_address: str,
    data: dict,
):
    """Partially update identity data for wallet address."""
    if wallet_address not in identities:
        raise HTTPException(status_code=404, detail="Identity not found")

    # Partial update identity
    identity = identities[wallet_address]
    if "commitment" in data:
        identity.commitment = data["commitment"]
    if "verification_bitmap" in data:
        identity.verification_bitmap = data["verification_bitmap"]

    identity.updated_at = _get_timestamp()

    return ApiResponse(
        success=True,
        message="Identity patched",
        data=identity.model_dump()
    )


# --- Transaction Routes ---


@router.post("/transaction/prepare", response_model=ApiResponse, tags=["transaction"])
async def prepare_transaction(
    wallet_address: str,
    data: dict,
):
    """Prepare transaction for identity/asset operations (unsigned)."""
    # Mock transaction preparation
    # In production, this would call Solana service layer
    transaction_id = f"txn_{wallet_address[:8]}_{_get_timestamp()}"

    transaction_data = {
        "transaction_id": transaction_id,
        "wallet_address": wallet_address,
        "transaction_type": data.get("transaction_type"),
        "status": "pending",
        "created_at": _get_timestamp(),
        # In production, this would include unsigned transaction bytes
        "unsigned_tx": "unsigned_transaction_placeholder",
    }

    return ApiResponse(
        success=True,
        message="Transaction prepared",
        data=transaction_data
    )


@router.post("/transaction/submit", response_model=ApiResponse, tags=["transaction"])
async def submit_transaction(
    wallet_address: str,
    data: dict,
):
    """Submit signed transaction to Solana network."""
    signature = data.get("signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Signature required")

    # Mock transaction submission
    # In production, this would call Solana service layer to submit signed transaction
    transaction_data = {
        "transaction_id": f"txn_{wallet_address[:8]}_{_get_timestamp()}",
        "wallet_address": wallet_address,
        "transaction_type": data.get("transaction_type"),
        "signature": signature,
        "status": "confirmed",  # Mock status
        "created_at": _get_timestamp(),
    }

    # Update identity if transaction is for identity update
    if data.get("transaction_type") == "identity_update":
        if wallet_address in identities:
            identities[wallet_address].updated_at = _get_timestamp()

    return ApiResponse(
        success=True,
        message="Transaction submitted",
        data=transaction_data
    )


# --- Credentials Routes ---


@router.get("/credentials/{wallet_address}", response_model=ApiResponse, tags=["credentials"])
async def get_credentials(
    wallet_address: str,
):
    """Get all credentials for a wallet address."""
    if wallet_address not in credentials:
        # Initialize empty credentials list for wallet
        credentials[wallet_address] = {}

    return ApiResponse(
        success=True,
        message="Credentials retrieved",
        data={
            "wallet_address": wallet_address,
            "credentials": [cred.model_dump() for cred in credentials[wallet_address].values()]
        }
    )


@router.post("/credentials/{wallet_address}", response_model=ApiResponse, tags=["credentials"])
async def issue_credential(
    wallet_address: str,
    request: CredentialRequest,
):
    """Issue a new credential to a wallet address."""
    # Initialize credentials dict for wallet if not exists
    if wallet_address not in credentials:
        credentials[wallet_address] = {}

    # Generate credential ID
    credential_id = f"cred_{wallet_address[:8]}_{int(time.time())}"

    # Create new credential
    credential = Credential(
        id=credential_id,
        type=request.type,
        issuer=f"did:aadharcha",  # Mock issuer DID
        subject=f"did:{wallet_address}",
        issuance_date=int(time.time()),
        expiration_date=None,  # Credentials are non-expiring for now
        revoked=False,
        claims=request.claims,
    )

    # Store credential
    credentials[wallet_address][credential_id] = credential

    # Update identity verification bitmap if needed
    if wallet_address in identities:
        identity = identities[wallet_address]
        if request.type == "aadhaar":
            identity.verification_bitmap |= 0b001  # Set bit 0
        elif request.type == "pan":
            identity.verification_bitmap |= 0b010  # Set bit 1
        identity.updated_at = _get_timestamp()

    return ApiResponse(
        success=True,
        message="Credential issued",
        data=credential.model_dump()
    )


@router.delete("/credentials/{wallet_address}/{credential_id}", response_model=ApiResponse, tags=["credentials"])
async def revoke_credential(
    wallet_address: str,
    credential_id: str,
):
    """Revoke a credential by ID."""
    if wallet_address not in credentials:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if credential_id not in credentials[wallet_address]:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Mark credential as revoked (don't delete, to maintain audit trail)
    credentials[wallet_address][credential_id].revoked = True

    return ApiResponse(
        success=True,
        message="Credential revoked",
        data={
            "credential_id": credential_id,
            "revoked": True,
        }
    )


# --- Helper Functions ---


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
