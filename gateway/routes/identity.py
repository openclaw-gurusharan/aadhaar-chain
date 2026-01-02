from fastapi import APIRouter, HTTPException
from models.identity import IdentityResponse, CreateIdentityRequest, UpdateIdentityRequest
from models.common import ApiResponse, UnsignedTransaction
from services.solana import solana_service

router = APIRouter(prefix="/identity", tags=["Identity"])


@router.get("/{wallet_address}", response_model=ApiResponse[IdentityResponse])
async def get_identity(wallet_address: str):
    try:
        account = await solana_service.get_identity_account(wallet_address)

        if not account:
            return ApiResponse(
                success=False,
                error="Identity not found",
            )

        return ApiResponse(
            success=True,
            data=IdentityResponse(
                did=wallet_address,
                owner=wallet_address,
                commitment="",
                verification_bitmap=0,
                credentials_verified=[],
                created_at=0,
                updated_at=0,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{wallet_address}", response_model=ApiResponse[UnsignedTransaction])
async def create_identity(wallet_address: str, request: CreateIdentityRequest):
    try:
        pda, bump = solana_service.derive_identity_pda(wallet_address)

        return ApiResponse(
            success=True,
            data=UnsignedTransaction(
                transaction="mock_unsigned_tx",
                blockhash="mock_blockhash",
                last_valid_block_height=0,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{wallet_address}", response_model=ApiResponse[UnsignedTransaction])
async def update_identity(wallet_address: str, request: UpdateIdentityRequest):
    try:
        return ApiResponse(
            success=True,
            data=UnsignedTransaction(
                transaction="mock_unsigned_tx",
                blockhash="mock_blockhash",
                last_valid_block_height=0,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
