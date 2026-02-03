"""Routes for identity operations."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models import (
    IdentityData,
    VerificationStatus,
    VerificationStep,
    VerificationStepDetail,
    StepStatus,
    AadhaarVerificationData,
    PanVerificationData,
    ApiResponse,
)


# In-memory stores (for development)
verifications: dict[str, VerificationStatus] = {}
identities: dict[str, IdentityData] = {}


router = APIRouter(prefix="/api/identity", tags=["identity"])


# --- Verification Routes ---


@router.post("/{wallet_address}/aadhaar", response_model=ApiResponse, tags=["identity"])
async def create_aadhaar_verification(
    wallet_address: str,
    data: AadhaarVerificationData
):
    """Create Aadhaar card verification request."""
    verification_id = f"aadhaar_{wallet_address}"

    # Initialize verification status with detailed steps
    status = VerificationStatus(
        verification_id=verification_id,
        wallet_address=wallet_address,
        status="processing",
        current_step=VerificationStep.document_received,
        steps=[
            VerificationStepDetail(name="document_received", status=StepStatus.completed),
            VerificationStepDetail(name="parsing", status=StepStatus.pending),
            VerificationStepDetail(name="fraud_check", status=StepStatus.pending),
            VerificationStepDetail(name="compliance_check", status=StepStatus.pending),
            VerificationStepDetail(name="blockchain_upload", status=StepStatus.pending),
            VerificationStepDetail(name="complete", status=StepStatus.pending),
        ],
        progress=0.0,
        created_at=_get_timestamp(),
        updated_at=_get_timestamp(),
    )

    verifications[verification_id] = status

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
    """Create PAN card verification request."""
    verification_id = f"pan_{wallet_address}"

    # Initialize verification status with detailed steps
    status = VerificationStatus(
        verification_id=verification_id,
        wallet_address=wallet_address,
        status="processing",
        current_step=VerificationStep.document_received,
        steps=[
            VerificationStepDetail(name="document_received", status=StepStatus.completed),
            VerificationStepDetail(name="parsing", status=StepStatus.pending),
            VerificationStepDetail(name="fraud_check", status=StepStatus.pending),
            VerificationStepDetail(name="compliance_check", status=StepStatus.pending),
            VerificationStepDetail(name="blockchain_upload", status=StepStatus.pending),
            VerificationStepDetail(name="complete", status=StepStatus.pending),
        ],
        progress=0.0,
        created_at=_get_timestamp(),
        updated_at=_get_timestamp(),
    )

    verifications[verification_id] = status

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
    if verification_id not in verifications:
        raise HTTPException(status_code=404, detail="Verification not found")

    return ApiResponse(
        success=True,
        data=verifications[verification_id].model_dump()
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
            did=f"did:sol:{wallet_address}",
            owner=wallet_address,
            commitment="",  # Will be set on blockchain
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
