"""Pydantic models for identity, verification, and credentials."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from enum import Enum


# --- Base Models ---


class ApiResponse(BaseModel):
    """Wrapper for consistent API responses."""
    success: bool = True
    message: str
    data: Optional[dict] = None


# --- Verification Models ---


class VerificationStep(str, Enum):
    """Verification workflow steps."""
    document_received = "document_received"
    parsing = "parsing"
    fraud_check = "fraud_check"
    compliance_check = "compliance_check"
    blockchain_upload = "blockchain_upload"
    complete = "complete"


class VerificationStatus(BaseModel):
    """Status of verification process."""
    verification_id: str
    wallet_address: str
    current_step: VerificationStep
    steps: List[VerificationStep] = []
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: str
    updated_at: str


# --- Identity Models ---


class IdentityData(BaseModel):
    """Identity data on blockchain."""
    did: str  # Decentralized Identifier
    wallet_address: str
    verification_bitmap: int = Field(default=0, ge=0)  # Bitmask of verified credential types
    created_at: str
    updated_at: str


# --- Verification Request Models ---


class AadhaarVerificationData(BaseModel):
    """Aadhaar card verification request."""
    name: str
    dob: str
    uid: str
    address: Optional[str] = None


class PanVerificationData(BaseModel):
    """PAN card verification request."""
    name: str
    pan_number: str = Field(min_length=10, max_length=10, pattern=r"^[A-Z]{5}[0-9]{4}$")
    dob: str


# --- Credential Models ---


class CredentialClaim(BaseModel):
    """Claim on a verifiable credential."""
    claim_type: str  # e.g., "name", "age", "nationality"
    claim_value: str  # The value of the claim
    verified_at: Optional[str] = None  # When this claim was verified


class Credential(BaseModel):
    """Verifiable credential."""
    credential_id: str
    wallet_address: str
    credential_type: str  # e.g., "aadhaar", "pan", "driving_license"
    claims: List[CredentialClaim]
    issued_at: str
    expires_at: Optional[str] = None
    revoked: bool = False


# --- Transaction Models ---


class TransactionData(BaseModel):
    """Transaction for identity/asset operations."""
    transaction_id: str
    wallet_address: str
    transaction_type: str  # "identity_create", "credential_issue", etc.
    amount: Optional[int] = None
    status: str  # "pending", "confirmed", "failed"
    created_at: str
