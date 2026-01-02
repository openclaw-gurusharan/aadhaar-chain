from fastapi import APIRouter, HTTPException
from models.credentials import AccessGrant
from models.common import ApiResponse
from datetime import datetime
import secrets

router = APIRouter(prefix="/grants", tags=["Access Grants"])


_grants_store: dict[str, list[dict]] = {}


@router.post("/{wallet_address}", response_model=ApiResponse[AccessGrant])
async def create_access_grant(wallet_address: str, request: dict):
    try:
        credential_id = request.get("credential_id")
        granted_to = request.get("granted_to")
        fields = request.get("fields", [])
        purpose = request.get("purpose", "")
        duration_hours = request.get("duration_hours", 24)

        if not credential_id or not granted_to:
            raise HTTPException(
                status_code=400, detail="credential_id and granted_to are required"
            )

        grant_id = secrets.token_hex(8)
        expires_at = int(datetime.now().timestamp()) + (duration_hours * 3600)
        created_at = int(datetime.now().timestamp())

        grant = {
            "grant_id": grant_id,
            "credential_id": credential_id,
            "granted_to": granted_to,
            "fields": fields,
            "purpose": purpose,
            "expires_at": expires_at,
            "created_at": created_at,
            "revoked_at": None,
        }

        if wallet_address not in _grants_store:
            _grants_store[wallet_address] = []
        _grants_store[wallet_address].append(grant)

        return ApiResponse(success=True, data=AccessGrant(**grant))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{wallet_address}", response_model=ApiResponse[list[AccessGrant]])
async def list_grants(wallet_address: str):
    try:
        now = int(datetime.now().timestamp())
        grants = _grants_store.get(wallet_address, [])

        active_grants = [
            g
            for g in grants
            if g["revoked_at"] is None and g["expires_at"] > now
        ]

        return ApiResponse(success=True, data=[AccessGrant(**g) for g in active_grants])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{wallet_address}/{grant_id}", response_model=ApiResponse[dict])
async def revoke_grant(wallet_address: str, grant_id: str):
    try:
        grants = _grants_store.get(wallet_address, [])
        grant = next((g for g in grants if g["grant_id"] == grant_id), None)

        if not grant:
            raise HTTPException(status_code=404, detail="Grant not found")

        grant["revoked_at"] = int(datetime.now().timestamp())

        return ApiResponse(success=True, data={"message": "Grant revoked"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
