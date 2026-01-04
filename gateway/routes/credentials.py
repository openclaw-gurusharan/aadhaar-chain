"""
Credential routes with 3-step OTP flow and mock mode support.

Flow:
1. POST /credentials/{wallet_address}/initiate - Send OTP (or mock OTP)
2. POST /credentials/{wallet_address}/verify - Verify OTP and return preview data
3. POST /credentials/{wallet_address}/confirm - Store credential in database
"""

from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from models.credentials import CredentialResponse, CredentialData
from models.common import ApiResponse
from services.apisetu import apisetu_client
from services.pda import pda_service
from database import get_db
from repositories.credential_repo import CredentialRepository
from config import settings
import hashlib
import uuid
import json

router = APIRouter(prefix="/credentials", tags=["Credentials"])

# Default issuer DID
DEFAULT_ISSUER_DID = "did:solana:default-issuer"

# Mock OTP for testing (in production, use Redis/database)
MOCK_OTP = "123456"
_otp_sessions: dict[str, dict] = {}

# Mock credential data for testing
MOCK_CREDENTIAL_DATA = {
    "aadhaar": {
        "aadhaar_number": "XXXX-XXXX-1234",
        "name": "Test User",
        "dob": "1990-01-01",
        "gender": "Male",
        "address": "123 Test Street, Bangalore",
        "pincode": "560001",
    },
    "pan": {
        "pan_number": "ABCDE1234F",
        "name": "Test User",
        "father_name": "Father Name",
        "dob": "1990-01-01",
        "pan_status": "Active",
    },
    "dl": {
        "dl_number": "KA01201230012345",
        "name": "Test User",
        "dob": "1990-01-01",
        "address": "123 Test Street, Bangalore",
        "issue_date": "2020-01-01",
        "expiry_date": "2030-01-01",
        "vehicle_classes": ["MCWG", "LMV"],
    },
    "land": {
        "property_id": "PROP-12345",
        "owner_name": "Test User",
        "property_address": "123 Test Street, Bangalore",
        "area": "1200 sq.ft",
        "survey_number": "SN-123",
        "ownership_type": "Freehold",
    },
    "education": {
        "degree": "Bachelor of Engineering",
        "university": "Test University",
        "year": "2012",
        "roll_number": "123456",
        "student_name": "Test User",
        "specialization": "Computer Science",
    },
}


# ============ Request Models ============

class InitiateRequest(BaseModel):
    credential_type: str
    data: dict[str, Any]


class VerifyRequest(BaseModel):
    credential_type: str
    data: dict[str, Any]
    otp: str


class ConfirmRequest(BaseModel):
    credential_type: str
    data: dict[str, Any]
    otp: str


# ============ List Credentials ============

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
                issued_at=int(c.issued_at.timestamp()),
                expires_at=int(c.expiry.timestamp()) if c.expiry else None,
                claims_summary={},
            )
            for c in creds
        ]

        return ApiResponse(success=True, data=responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Step 1: Initiate OTP ============

@router.post("/{wallet_address}/initiate", response_model=ApiResponse[dict])
async def initiate_credential(
    wallet_address: str, request: InitiateRequest, db: AsyncSession = Depends(get_db)
):
    """Step 1: Initiate credential fetch by sending OTP."""
    try:
        credential_type = request.credential_type.lower()

        if credential_type not in MOCK_CREDENTIAL_DATA:
            raise ValueError(f"Unknown credential type: {credential_type}")

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Store session data
        _otp_sessions[session_id] = {
            "wallet_address": wallet_address,
            "credential_type": credential_type,
            "form_data": request.data,
            "timestamp": datetime.now().isoformat(),
        }

        # In mock mode, return the OTP in response (for testing)
        if settings.mock_mode:
            return ApiResponse(
                success=True,
                data={
                    "message": "OTP initiated (mock mode)",
                    "session_id": session_id,
                    "otp": MOCK_OTP,  # Only in mock mode
                    "mock_mode": True,
                },
            )
        else:
            # In production, API Setu sends real OTP to mobile
            return ApiResponse(
                success=True,
                data={
                    "message": "OTP sent to registered mobile",
                    "session_id": session_id,
                    "mock_mode": False,
                },
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Step 2: Verify OTP and Return Preview ============

@router.post("/{wallet_address}/verify", response_model=ApiResponse[dict])
async def verify_otp(
    wallet_address: str, request: VerifyRequest, db: AsyncSession = Depends(get_db)
):
    """Step 2: Verify OTP and return credential data for preview."""
    try:
        credential_type = request.credential_type.lower()

        # Mock OTP verification
        if settings.mock_mode:
            if request.otp != MOCK_OTP:
                raise HTTPException(status_code=401, detail="Invalid OTP")
            # Use mock data
            credential_data = MOCK_CREDENTIAL_DATA.get(credential_type)
        else:
            # In production, call API Setu with OTP
            if credential_type == "aadhaar":
                credential_data = await apisetu_client.fetch_aadhaar(
                    request.data.get("aadhaar_number", ""), request.otp
                )
            elif credential_type == "pan":
                credential_data = await apisetu_client.fetch_pan(
                    request.data.get("pan_number", "")
                )
            elif credential_type == "dl":
                credential_data = await apisetu_client.fetch_driving_license(
                    request.data.get("dl_number", ""),
                    request.data.get("dob", "")
                )
            elif credential_type == "land":
                credential_data = await apisetu_client.fetch_land_records(
                    request.data.get("state", ""),
                    request.data.get("district", ""),
                    request.data.get("survey_number", "")
                )
            elif credential_type == "education":
                credential_data = await apisetu_client.fetch_education(
                    request.data.get("roll_number", ""),
                    request.data.get("year", 0),
                    request.data.get("board", "")
                )
            else:
                raise ValueError(f"Unknown credential type: {credential_type}")

        return ApiResponse(
            success=True,
            data={
                "message": "OTP verified, please preview and confirm",
                "credential_data": credential_data,
                "credential_type": credential_type,
            },
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Step 3: Confirm and Store ============

@router.post("/{wallet_address}/confirm", response_model=ApiResponse[CredentialResponse])
async def confirm_credential(
    wallet_address: str, request: ConfirmRequest, db: AsyncSession = Depends(get_db)
):
    """Step 3: Confirm and store credential in database."""
    try:
        credential_type = request.credential_type.lower()

        # Final OTP verification
        if settings.mock_mode:
            if request.otp != MOCK_OTP:
                raise HTTPException(status_code=401, detail="Invalid OTP")
            credential_data = MOCK_CREDENTIAL_DATA.get(credential_type, {})
        else:
            # Re-verify with API Setu and get final data
            if credential_type == "aadhaar":
                credential_data = await apisetu_client.fetch_aadhaar(
                    request.data.get("aadhaar_number", ""), request.otp
                )
            elif credential_type == "pan":
                credential_data = await apisetu_client.fetch_pan(
                    request.data.get("pan_number", "")
                )
            elif credential_type == "dl":
                credential_data = await apisetu_client.fetch_driving_license(
                    request.data.get("dl_number", ""),
                    request.data.get("dob", "")
                )
            elif credential_type == "land":
                credential_data = await apisetu_client.fetch_land_records(
                    request.data.get("state", ""),
                    request.data.get("district", ""),
                    request.data.get("survey_number", "")
                )
            elif credential_type == "education":
                credential_data = await apisetu_client.fetch_education(
                    request.data.get("roll_number", ""),
                    request.data.get("year", 0),
                    request.data.get("board", "")
                )
            else:
                raise ValueError(f"Unknown credential type: {credential_type}")

        # Derive PDA
        pda_address, bump = pda_service.derive_credential_pda(
            wallet_address=wallet_address,
            credential_type=credential_type,
            issuer_did=DEFAULT_ISSUER_DID,
        )

        # Create credential hash
        cred_id = str(uuid.uuid4())
        claims_hash = hashlib.sha256(json.dumps(credential_data, sort_keys=True).encode()).digest()

        # In mock mode, ensure identity exists (foreign key constraint)
        if settings.mock_mode:
            from repositories.identity_repo import IdentityRepository
            identity_repo = IdentityRepository(db)
            existing = await identity_repo.get(wallet_address)
            if not existing:
                # Create dummy identity for testing
                identity_pda, identity_bump = pda_service.derive_identity_pda(wallet_address)
                await identity_repo.create(
                    wallet_address=wallet_address,
                    pda_address=identity_pda,
                    owner_pubkey=wallet_address,
                    bump=identity_bump,
                )

        # Store in database
        repo = CredentialRepository(db)
        credential = await repo.create(
            credential_id=cred_id,
            pda_address=pda_address,
            owner_wallet=wallet_address,
            credential_type=credential_type,
            claims_hash=claims_hash,
            issuer_did=DEFAULT_ISSUER_DID,
            issued_at=datetime.now(),
            bump=bump,
        )

        await db.commit()

        return ApiResponse(
            success=True,
            data=CredentialResponse(
                credential_id=credential.credential_id,
                credential_type=credential.credential_type,
                status="active",
                issued_at=int(credential.issued_at.timestamp()),
                expires_at=int(credential.expiry.timestamp()) if credential.expiry else None,
                claims_summary=credential_data,
            ),
        )

    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Legacy Single-Step Endpoint ============

@router.post("/{wallet_address}", response_model=ApiResponse[CredentialResponse])
async def fetch_and_tokenize_credential(
    wallet_address: str, request: CredentialData, db: AsyncSession = Depends(get_db)
):
    """Legacy endpoint for single-step credential fetch (use /initiate -> /verify -> /confirm instead)."""
    try:
        # For mock mode, directly use mock data
        if settings.mock_mode:
            credential_data = MOCK_CREDENTIAL_DATA.get(request.credential_type, {})
        else:
            # Fetch from API Setu
            match request.credential_type:
                case "aadhaar":
                    credential_data = await apisetu_client.fetch_aadhaar(
                        request.data.aadhaar_number
                    )
                case "pan":
                    credential_data = await apisetu_client.fetch_pan(request.data.pan_number)
                case "dl":
                    credential_data = await apisetu_client.fetch_driving_license(
                        request.data.dl_number, request.data.dob
                    )
                case "land":
                    credential_data = await apisetu_client.fetch_land_records(
                        "", "", request.data.survey_number
                    )
                case "education":
                    credential_data = await apisetu_client.fetch_education(
                        request.data.roll_number, request.data.year, ""
                    )
                case _:
                    raise ValueError(f"Unknown credential type: {request.credential_type}")

        # Derive PDA
        pda_address, bump = pda_service.derive_credential_pda(
            wallet_address=wallet_address,
            credential_type=request.credential_type,
            issuer_did=DEFAULT_ISSUER_DID,
        )

        # Create credential
        cred_id = str(uuid.uuid4())
        claims_hash = hashlib.sha256(json.dumps(credential_data, sort_keys=True).encode()).digest()

        # In mock mode, ensure identity exists (foreign key constraint)
        if settings.mock_mode:
            from repositories.identity_repo import IdentityRepository
            identity_repo = IdentityRepository(db)
            existing = await identity_repo.get(wallet_address)
            if not existing:
                # Create dummy identity for testing
                identity_pda, identity_bump = pda_service.derive_identity_pda(wallet_address)
                await identity_repo.create(
                    wallet_address=wallet_address,
                    pda_address=identity_pda,
                    owner_pubkey=wallet_address,
                    bump=identity_bump,
                )

        repo = CredentialRepository(db)
        credential = await repo.create(
            credential_id=cred_id,
            pda_address=pda_address,
            owner_wallet=wallet_address,
            credential_type=request.credential_type,
            claims_hash=claims_hash,
            issuer_did=DEFAULT_ISSUER_DID,
            issued_at=request.fetched_at or datetime.now(),
            bump=bump,
        )

        await db.commit()

        return ApiResponse(
            success=True,
            data=CredentialResponse(
                credential_id=credential.credential_id,
                credential_type=credential.credential_type,
                status="active",
                issued_at=int(credential.issued_at.timestamp()),
                expires_at=int(credential.expiry.timestamp()) if credential.expiry else None,
                claims_summary=credential_data,
            ),
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Get Single Credential ============

@router.get("/{wallet_address}/{credential_type}", response_model=ApiResponse[CredentialResponse])
async def get_credential(
    wallet_address: str, credential_type: str, db: AsyncSession = Depends(get_db)
):
    try:
        repo = CredentialRepository(db)
        creds = await repo.list_by_type(wallet_address, credential_type)

        if not creds:
            raise HTTPException(status_code=404, detail="Credential not found")

        cred = creds[0]
        return ApiResponse(
            success=True,
            data=CredentialResponse(
                credential_id=cred.credential_id,
                credential_type=cred.credential_type,
                status="active" if not cred.revoked else "revoked",
                issued_at=int(cred.issued_at.timestamp()),
                expires_at=int(cred.expiry.timestamp()) if cred.expiry else None,
                claims_summary={},
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Revoke Credential ============

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
