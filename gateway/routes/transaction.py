from fastapi import APIRouter, HTTPException
from models.common import ApiResponse, UnsignedTransaction, SignedTransaction, TransactionReceipt
from models.common import ErrorResponse
from services.solana import solana_service

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post("/prepare", response_model=ApiResponse[UnsignedTransaction])
async def prepare_transaction(request: dict):
    try:
        instructions = request.get("instructions")
        payer = request.get("payer")

        if not instructions or not payer:
            raise HTTPException(
                status_code=400, detail="instructions and payer are required"
            )

        result = await solana_service.prepare_transaction(instructions, payer)

        return ApiResponse(
            success=True,
            data=UnsignedTransaction(**result),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=ApiResponse[TransactionReceipt])
async def submit_transaction(request: SignedTransaction):
    try:
        result = await solana_service.submit_transaction(request.transaction)

        return ApiResponse(
            success=True,
            data=TransactionReceipt(
                signature=result["signature"],
                slot=0,
                confirmations=1,
                status="success",
            ),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=str(e),
            data=TransactionReceipt(
                signature="",
                slot=0,
                confirmations=0,
                status="failed",
                error=str(e),
            ),
        )
