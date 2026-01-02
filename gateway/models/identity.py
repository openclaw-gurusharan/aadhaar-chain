from pydantic import BaseModel, Field
from typing import Optional


class Identity(BaseModel):
    did: str = Field(..., description="Decentralized Identifier")
    owner: str = Field(..., description="Wallet address")
    commitment: str = Field(..., description="Hash commitment for key rotation")
    verification_bitmap: int = Field(default=0, description="Bit flags for verified credentials")
    created_at: int = Field(..., description="Unix timestamp")
    updated_at: int = Field(..., description="Unix timestamp")


class CreateIdentityRequest(BaseModel):
    did: Optional[str] = Field(None, description="Auto-generated if not provided")
    commitment: Optional[str] = Field(None, description="Hash for initial commitment")


class UpdateIdentityRequest(BaseModel):
    new_commitment: str = Field(..., description="New hash commitment for key rotation")


class IdentityResponse(BaseModel):
    did: str
    owner: str
    commitment: str
    verification_bitmap: int
    credentials_verified: list[str] = Field(default_factory=list)
    created_at: int
    updated_at: int
