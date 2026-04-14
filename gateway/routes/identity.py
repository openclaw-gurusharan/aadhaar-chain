from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.identity import IdentityResponse, CreateIdentityRequest, UpdateIdentityRequest
from models.common import ApiResponse, UnsignedTransaction
from services.solana import solana_service
from services.pda import PDAService
from database import get_db, is_db_available
from repositories.identity_repo import IdentityRepository

router = APIRouter(prefix="/identity", tags=["Identity"])


def _trust_surface(identity: IdentityResponse) -> dict:
    verification_bitmap = identity.verification_bitmap or 0
    trust_state = "verified" if verification_bitmap > 0 else "identity_present_unverified"
    state_reason = (
        "Verification approved and available for downstream use."
        if trust_state == "verified"
        else "Identity anchor exists, but no approved verification is available yet."
    )
    return {
        "trust_version": "v1",
        "wallet_address": identity.owner,
        "did": identity.did,
        "verification_bitmap": verification_bitmap,
        "updated_at": identity.updated_at,
        "trust_state": trust_state,
        "high_trust_eligible": trust_state == "verified",
        "state_reason": state_reason,
        "verifications": [],
    }


@router.get("/{wallet_address}", response_model=ApiResponse[IdentityResponse])
async def get_identity(wallet_address: str, db: AsyncSession = Depends(get_db)):
    if not is_db_available():
        return ApiResponse(
            success=True,
            message="Identity store unavailable in degraded mode.",
            data=None,
        )

    try:
        repo = IdentityRepository(db)
        identity = await repo.get(wallet_address)

        if not identity:
            return ApiResponse(
                success=True,
                message="Identity not found",
                data=None,
            )

        return ApiResponse(
            success=True,
            data=IdentityResponse(
                did=wallet_address,
                owner=identity.owner_pubkey,
                commitment=identity.commitment_hash.hex() if identity.commitment_hash else "",
                verification_bitmap=identity.verification_bits,
                credentials_verified=[],
                created_at=int(identity.created_at.timestamp()),
                updated_at=int(identity.updated_at.timestamp()),
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{wallet_address}/trust", response_model=ApiResponse[dict])
async def get_identity_trust(wallet_address: str, db: AsyncSession = Depends(get_db)):
    if not is_db_available():
        return ApiResponse(
            success=True,
            message="Identity store unavailable in degraded mode.",
            data=None,
        )

    try:
        repo = IdentityRepository(db)
        identity = await repo.get(wallet_address)

        if not identity:
            return ApiResponse(
                success=True,
                message="Identity not found",
                data=None,
            )

        identity_response = IdentityResponse(
            did=wallet_address,
            owner=identity.owner_pubkey,
            commitment=identity.commitment_hash.hex() if identity.commitment_hash else "",
            verification_bitmap=identity.verification_bits,
            credentials_verified=[],
            created_at=int(identity.created_at.timestamp()),
            updated_at=int(identity.updated_at.timestamp()),
        )

        return ApiResponse(success=True, data=_trust_surface(identity_response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{wallet_address}", response_model=ApiResponse[dict])
async def create_identity(
    wallet_address: str, request: CreateIdentityRequest, db: AsyncSession = Depends(get_db)
):
    try:
        # Check if identity already exists
        repo = IdentityRepository(db)
        existing = await repo.get(wallet_address)
        if existing:
            raise HTTPException(status_code=409, detail="Identity already exists")

        # Derive PDA
        pda_service = PDAService()
        pda, bump = pda_service.derive_identity_pda(wallet_address)

        # Create identity in database
        identity = await repo.create(
            wallet_address=wallet_address,
            pda_address=pda,
            owner_pubkey=request.owner_pubkey or wallet_address,
            bump=bump,
            commitment_hash=None,
            metadata_uri=request.metadata_uri,
        )
        await db.commit()

        return ApiResponse(
            success=True,
            data={
                "wallet_address": identity.wallet_address,
                "pda_address": identity.pda_address,
                "bump": identity.bump,
                "created_at": identity.created_at.isoformat(),
            },
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{wallet_address}", response_model=ApiResponse[dict])
async def update_identity(
    wallet_address: str, request: UpdateIdentityRequest, db: AsyncSession = Depends(get_db)
):
    try:
        repo = IdentityRepository(db)
        identity = await repo.get(wallet_address)

        if not identity:
            raise HTTPException(status_code=404, detail="Identity not found")

        # Update identity
        updated = await repo.update(
            wallet_address=wallet_address,
            commitment_hash=request.commitment_hash.encode() if request.commitment_hash else None,
            metadata_uri=request.metadata_uri,
            recovery_counter=request.recovery_counter,
        )
        await db.commit()

        return ApiResponse(
            success=True,
            data={
                "wallet_address": updated.wallet_address,
                "pda_address": updated.pda_address,
                "updated_at": updated.updated_at.isoformat(),
            },
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
