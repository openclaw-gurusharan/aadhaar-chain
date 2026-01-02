from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class VerificationStep(BaseModel):
    name: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    message: Optional[str] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None


class VerificationStatus(BaseModel):
    verification_id: str
    wallet_address: str
    credential_type: Literal["aadhaar", "pan", "dl", "land", "education"]
    overall_status: Literal["pending", "processing", "verified", "failed"]
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    steps: list[VerificationStep]
    error: Optional[str] = None
    created_at: int
    updated_at: int


class TokenizationRequest(BaseModel):
    credential_type: Literal["aadhaar", "pan", "dl", "land", "education"]
    credential_data: dict
    expiry_days: Optional[int] = Field(None, ge=1, le=365)


class TokenizationStatus(BaseModel):
    tokenization_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: int = Field(..., ge=0, le=100)
    transaction_id: Optional[str] = None
    credential_token_id: Optional[str] = None
    error: Optional[str] = None
