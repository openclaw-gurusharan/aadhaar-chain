"""Pydantic models for identity, verification, and credentials."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal, Dict, Any
from enum import Enum


# --- Base Models ---


class ApiResponse(BaseModel):
    """Wrapper for consistent API responses."""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ApiError(BaseModel):
    """API error details."""
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None


# --- Verification Models ---


class VerificationStep(str, Enum):
    """Verification workflow steps."""
    document_received = "document_received"
    parsing = "parsing"
    fraud_check = "fraud_check"
    compliance_check = "compliance_check"
    blockchain_upload = "blockchain_upload"
    complete = "complete"


class StepStatus(str, Enum):
    """Status of individual verification step."""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class VerificationStepDetail(BaseModel):
    """Detailed verification step with status."""
    name: str
    status: StepStatus


class VerificationStatus(BaseModel):
    """Status of verification process."""
    verification_id: str
    wallet_address: str
    status: Literal["pending", "processing", "verified", "failed"]
    current_step: Optional[VerificationStep] = None
    steps: List[VerificationStepDetail] = []
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: str
    updated_at: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# --- Identity Models ---


class IdentityData(BaseModel):
    """Identity data on blockchain - matches frontend Identity interface."""
    did: str  # Decentralized Identifier
    owner: str  # Wallet address that owns this identity
    commitment: str  # Hash commitment on chain
    verification_bitmap: int = Field(default=0, ge=0)  # Bitmask of verified credential types
    created_at: str  # ISO timestamp
    updated_at: str  # ISO timestamp


class CreateIdentityRequest(BaseModel):
    """Request to create a new identity."""
    commitment: str


class CreateIdentityResponse(BaseModel):
    """Response after creating identity."""
    identity: IdentityData
    signature: Optional[str] = None


# --- Verification Request Models ---


class AadhaarVerificationData(BaseModel):
    """Aadhaar card verification request."""
    name: str
    dob: str
    uid: str
    address: Optional[str] = None
    document_hash: Optional[str] = None


class PanVerificationData(BaseModel):
    """PAN card verification request."""
    name: str
    pan_number: str = Field(min_length=10, max_length=10, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$")
    dob: str
    document_hash: Optional[str] = None


class VerificationRequest(BaseModel):
    """Generic verification request."""
    document_type: Literal["aadhaar", "pan"]
    document_data: str  # Base64 encoded or hash


class VerificationResponse(BaseModel):
    """Response after initiating verification."""
    success: bool
    verification_id: str
    status: Literal["pending", "processing", "verified", "failed"]
    message: str


# --- Credential Models ---


class CredentialClaim(BaseModel):
    """Claim on a verifiable credential - flexible key-value structure."""
    claim_type: str  # e.g., "name", "age", "nationality"
    claim_value: str  # The value of the claim
    verified_at: Optional[str] = None  # When this claim was verified


class Credential(BaseModel):
    """Verifiable credential - matches frontend Credential interface."""
    id: str  # Credential identifier
    type: str  # e.g., "aadhaar", "pan", "driving_license"
    issuer: str  # DID of the issuer
    subject: str  # DID of the subject (user)
    issuance_date: int  # Unix timestamp
    expiration_date: Optional[int] = None  # Unix timestamp
    revoked: bool = False
    claims: Dict[str, Any]  # Flexible claims structure


class CredentialRequest(BaseModel):
    """Request to issue a new credential."""
    type: str
    claims: Dict[str, Any]


# --- Wallet Models ---


class WalletBalance(BaseModel):
    """Wallet SOL balance."""
    lamports: int
    sol: float


# --- Transaction Models ---


class TransactionData(BaseModel):
    """Transaction for identity/asset operations."""
    transaction_id: str
    wallet_address: str
    transaction_type: Literal["identity_create", "credential_issue", "identity_update", "credential_revoke"]
    amount: Optional[int] = None
    status: Literal["pending", "confirmed", "failed"]
    created_at: str
    signature: Optional[str] = None  # Solana transaction signature


class TransactionResponse(BaseModel):
    """Response after transaction submission."""
    signature: str
    success: bool
    error: Optional[str] = None


# --- Transaction Request Models ---


class PrepareTransactionRequest(BaseModel):
    """Request to prepare a transaction (unsigned)."""
    wallet_address: str
    transaction_type: Literal["identity_create", "credential_issue", "identity_update", "credential_revoke"]
    data: Optional[Dict[str, Any]] = None


class SubmitTransactionRequest(BaseModel):
    """Request to submit a signed transaction."""
    wallet_address: str
    signature: str
    transaction_type: str


# --- Additional Helper Models ---


class StatusUpdate(BaseModel):
    """Generic status update."""
    verification_id: str
    status: Literal["pending", "processing", "verified", "failed"]
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    error: Optional[str] = None
