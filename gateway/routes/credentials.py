from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.credentials import CredentialResponse, CredentialData
from models.common import ApiResponse
from services.apisetu import apisetu_client
from database import get_db
from repositories.credential_repo import CredentialRepository
import hashlib
import uuid

router = APIRouter(prefix="/credentials", tags=["Credentials"])


@router.get("/{wallet_address}", response_model=ApiResponse[list[CredentialResponse]])
async def list_credentials(wallet_address: str, db: AsyncSession = Depends(get_db)):
    try:
        repo = CredentialRepository(db)
        creds = await repo.list_by_owner(wallet_address)

        responses = [
            CredentialResponse(
                credential_id=c.credential_id,
                credential_type=c.credential_type,
                status="active" if not c.revoked else "revoked",
                issued_at=c.issued_at,
                expires_at=c.expiry,
                claims_summary={},  # Claims are stored as hash, not full data
            )
            for c in creds
        ]

        return ApiResponse(success=True, data=responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{wallet_address}", response_model=ApiResponse[CredentialResponse])
async def fetch_and_tokenize_credential(
    wallet_address: str, request: CredentialData, db: AsyncSession = Depends(get_db)
):
    try:
        match request.credential_type:
            case "aadhaar":
                data = await apisetu_client.fetch_aadhaar(
                    request.data.aadhaar_number
                )
            case "pan":
                data = await apisetu_client.fetch_pan(request.data.pan_number)
            case "dl":
                data = await apisetu_client.fetch_driving_license(
                    request.data.dl_number, request.data.dob
                )
            case "land":
                data = await apisetu_client.fetch_land_records(
                    "", "", request.data.survey_number
                )
            case "education":
                data = await apisetu_client.fetch_education(
                    request.data.roll_number, request.data.year, ""
                )
            case _:
                raise ValueError(f"Unknown credential type: {request.credential_type}")

        # Create credential in database
        cred_id = str(uuid.uuid4())
        claims_hash = hashlib.sha256(str(data).encode()).digest()  # 32-byte hash

        repo = CredentialRepository(db)
        credential = await repo.create(
            credential_id=cred_id,
            pda_address=f"{wallet_address}-{request.credential_type}",  # Placeholder PDA
            owner_wallet=wallet_address,
            credential_type=request.credential_type,
            claims_hash=claims_hash,
            issued_at=request.fetched_at,
            bump=255,  # Placeholder bump
        )

        # Commit transaction
        await db.commit()

        return ApiResponse(
            success=True,
            data=CredentialResponse(
                credential_id=credential.credential_id,
                credential_type=credential.credential_type,
                status="active",
                issued_at=credential.issued_at,
                expires_at=credential.expiry,
                claims_summary={},
            ),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{wallet_address}/{credential_type}", response_model=ApiResponse[CredentialResponse])
async def get_credential(
    wallet_address: str, credential_type: str, db: AsyncSession = Depends(get_db)
):
    try:
        repo = CredentialRepository(db)
        creds = await repo.list_by_type(wallet_address, credential_type)

        if not creds:
            raise HTTPException(status_code=404, detail="Credential not found")

        cred = creds[0]  # Get the most recent
        return ApiResponse(
            success=True,
            data=CredentialResponse(
                credential_id=cred.credential_id,
                credential_type=cred.credential_type,
                status="active" if not cred.revoked else "revoked",
                issued_at=cred.issued_at,
                expires_at=cred.expiry,
                claims_summary={},
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{wallet_address}/{credential_id}", response_model=ApiResponse[dict])
async def revoke_credential(
    wallet_address: str, credential_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        repo = CredentialRepository(db)
        cred = await repo.get(credential_id)

        if not cred or cred.owner_wallet != wallet_address:
            raise HTTPException(status_code=404, detail="Credential not found")

        await repo.revoke(credential_id)
        await db.commit()

        return ApiResponse(success=True, data={"message": "Credential revoked"})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
