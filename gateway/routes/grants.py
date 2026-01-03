from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.credentials import AccessGrant
from models.common import ApiResponse
from database import get_db
from repositories.grant_repo import GrantRepository
from services.pda import PDAService
import secrets
import uuid

router = APIRouter(prefix="/grants", tags=["Access Grants"])


@router.post("/{wallet_address}", response_model=ApiResponse[dict])
async def create_access_grant(wallet_address: str, request: dict, db: AsyncSession = Depends(get_db)):
    try:
        credential_pda = request.get("credential_pda")
        granted_to = request.get("granted_to")
        purpose = request.get("purpose", "")
        duration_hours = request.get("duration_hours", 24)
        field_mask = request.get("field_mask", 0)

        if not credential_pda or not granted_to:
            raise HTTPException(
                status_code=400, detail="credential_pda and granted_to are required"
            )

        # Generate grant_id and derive PDA
        grant_id = secrets.token_hex(8)
        pda_service = PDAService()
        grant_pda, bump = pda_service.derive_grant_pda(
            credential_pda, wallet_address, purpose
        )

        # Calculate expiry
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)

        # Create grant in database
        repo = GrantRepository(db)
        grant = await repo.create(
            grant_id=grant_id,
            pda_address=grant_pda,
            credential_pda=credential_pda,
            grantor_wallet=wallet_address,
            grantee_wallet=granted_to,
            expires_at=expires_at,
            bump=bump,
            purpose=purpose,
            field_mask=field_mask,
        )
        await db.commit()

        return ApiResponse(
            success=True,
            data={
                "grant_id": grant.grant_id,
                "pda_address": grant.pda_address,
                "expires_at": grant.expires_at.isoformat(),
            },
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{wallet_address}", response_model=ApiResponse[list[dict]])
async def list_grants(wallet_address: str, db: AsyncSession = Depends(get_db)):
    try:
        repo = GrantRepository(db)
        grants = await repo.list_by_grantor(wallet_address, include_revoked=False)

        response_data = [
            {
                "grant_id": g.grant_id,
                "pda_address": g.pda_address,
                "credential_pda": g.credential_pda,
                "grantee_wallet": g.grantee_wallet,
                "expires_at": g.expires_at.isoformat(),
                "purpose": g.purpose,
            }
            for g in grants
            if g.expires_at > datetime.utcnow()
        ]

        return ApiResponse(success=True, data=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{wallet_address}/{grant_id}", response_model=ApiResponse[dict])
async def revoke_grant(wallet_address: str, grant_id: str, db: AsyncSession = Depends(get_db)):
    try:
        repo = GrantRepository(db)
        grant = await repo.get(grant_id)

        if not grant or grant.grantor_wallet != wallet_address:
            raise HTTPException(status_code=404, detail="Grant not found or unauthorized")

        await repo.revoke(grant_id)
        await db.commit()

        return ApiResponse(success=True, data={"message": "Grant revoked"})
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
