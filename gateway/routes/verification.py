from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.verification import VerificationStatus, TokenizationStatus
from models.common import ApiResponse
from datetime import datetime
from database import get_db
from repositories.verification_repo import VerificationRepository
import secrets
import uuid

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/{wallet_address}/status", response_model=ApiResponse[dict])
async def get_overall_status(wallet_address: str, db: AsyncSession = Depends(get_db)):
    try:
        repo = VerificationRepository(db)
        user_verifications = await repo.list_by_wallet(wallet_address)

        return ApiResponse(
            success=True,
            data={
                "wallet_address": wallet_address,
                "total_verifications": len(user_verifications),
                "verified_count": sum(
                    1 for v in user_verifications if v.overall_status == "verified"
                ),
                "verifications": [
                    {
                        "credential_type": v.credential_type,
                        "status": v.overall_status,
                        "progress": v.progress,
                    }
                    for v in user_verifications
                ],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{verification_id}", response_model=ApiResponse[VerificationStatus])
async def get_verification_status(
    verification_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        repo = VerificationRepository(db)
        verification = await repo.get(verification_id)

        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")

        return ApiResponse(success=True, data=VerificationStatus(**verification))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{wallet_address}/{credential_type}", response_model=ApiResponse[VerificationStatus])
async def start_verification(
    wallet_address: str, credential_type: str, db: AsyncSession = Depends(get_db)
):
    try:
        verification_id = str(uuid.uuid4())

        repo = VerificationRepository(db)
        verification = await repo.create(
            verification_id=verification_id,
            wallet_address=wallet_address,
            credential_type=credential_type,
            overall_status="pending",
            progress=0,
        )

        await db.commit()

        return ApiResponse(success=True, data=VerificationStatus(**verification))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{verification_id}/progress", response_model=ApiResponse[VerificationStatus])
async def update_verification_progress(
    verification_id: str, request: dict, db: AsyncSession = Depends(get_db)
):
    try:
        repo = VerificationRepository(db)
        verification = await repo.get(verification_id)

        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")

        progress = min(100, max(0, request.get("progress", verification.progress)))
        step_name = request.get("step_name")
        step_status = request.get("step_status", "pending")

        # Update overall status based on progress
        overall_status = "pending"
        if progress >= 100:
            overall_status = "verified"
        elif progress > 0:
            overall_status = "in_progress"

        await repo.update_status(verification_id, overall_status, progress)

        # Update specific step if provided
        if step_name:
            await repo.update_step_status(verification_id, step_name, step_status)

        await db.commit()

        # Fetch updated verification
        verification = await repo.get(verification_id)
        return ApiResponse(success=True, data=VerificationStatus(**verification))
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
