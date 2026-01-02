from fastapi import APIRouter, HTTPException
from models.verification import VerificationStatus, TokenizationStatus
from models.common import ApiResponse
from datetime import datetime
import secrets

router = APIRouter(prefix="/verification", tags=["Verification"])


_verifications: dict[str, dict] = {}


@router.get("/{wallet_address}/status", response_model=ApiResponse[dict])
async def get_overall_status(wallet_address: str):
    try:
        user_verifications = [
            v for v in _verifications.values() if v["wallet_address"] == wallet_address
        ]

        return ApiResponse(
            success=True,
            data={
                "wallet_address": wallet_address,
                "total_verifications": len(user_verifications),
                "verified_count": sum(
                    1 for v in user_verifications if v["overall_status"] == "verified"
                ),
                "verifications": [
                    {
                        "credential_type": v["credential_type"],
                        "status": v["overall_status"],
                        "progress": v["progress"],
                    }
                    for v in user_verifications
                ],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{verification_id}", response_model=ApiResponse[VerificationStatus])
async def get_verification_status(verification_id: str):
    try:
        verification = _verifications.get(verification_id)

        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")

        return ApiResponse(success=True, data=VerificationStatus(**verification))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{wallet_address}/{credential_type}", response_model=ApiResponse[VerificationStatus])
async def start_verification(wallet_address: str, credential_type: str):
    try:
        verification_id = secrets.token_hex(8)
        now = int(datetime.now().timestamp())

        steps = [
            {"name": "fetch_from_apisetu", "status": "pending", "message": None},
            {"name": "validate_data", "status": "pending", "message": None},
            {"name": "prepare_transaction", "status": "pending", "message": None},
            {"name": "tokenize_on_chain", "status": "pending", "message": None},
        ]

        verification = {
            "verification_id": verification_id,
            "wallet_address": wallet_address,
            "credential_type": credential_type,
            "overall_status": "pending",
            "progress": 0,
            "steps": steps,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

        _verifications[verification_id] = verification

        return ApiResponse(success=True, data=VerificationStatus(**verification))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{verification_id}/progress", response_model=ApiResponse[VerificationStatus])
async def update_verification_progress(
    verification_id: str, request: dict
):
    try:
        verification = _verifications.get(verification_id)

        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")

        progress = request.get("progress", 0)
        step_name = request.get("step_name")
        step_status = request.get("step_status", "pending")
        message = request.get("message")

        verification["progress"] = min(100, max(0, progress))
        verification["updated_at"] = int(datetime.now().timestamp())

        if step_name:
            for step in verification["steps"]:
                if step["name"] == step_name:
                    step["status"] = step_status
                    step["message"] = message
                    if step_status == "in_progress" and not step.get("started_at"):
                        step["started_at"] = int(datetime.now().timestamp())
                    if step_status == "completed":
                        step["completed_at"] = int(datetime.now().timestamp())
                    break

        if progress >= 100:
            verification["overall_status"] = "verified"
        elif progress > 0:
            verification["overall_status"] = "processing"

        return ApiResponse(success=True, data=VerificationStatus(**verification))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
