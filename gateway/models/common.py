from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, Literal


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")


class UnsignedTransaction(BaseModel):
    transaction: str = Field(..., description="Base64 encoded unsigned transaction")
    blockhash: str = Field(..., description="Recent blockhash")
    last_valid_block_height: int = Field(..., description="Transaction expiry block")


class SignedTransaction(BaseModel):
    transaction: str = Field(..., description="Base64 encoded signed transaction")


class TransactionReceipt(BaseModel):
    signature: str
    slot: int
    confirmations: int
    status: Literal["success", "failed"]
    error: Optional[str] = None
