from fastapi import APIRouter, HTTPException
from models.credentials import CredentialResponse, CredentialData
from models.common import ApiResponse
from services.apisetu import apisetu_client

router = APIRouter(prefix="/credentials", tags=["Credentials"])


_in_memory_store: dict[str, list[dict]] = {}


@router.get("/{wallet_address}", response_model=ApiResponse[list[CredentialResponse]])
async def list_credentials(wallet_address: str):
    try:
        creds = _in_memory_store.get(wallet_address, [])

        responses = [
            CredentialResponse(
                credential_id=c["credential_id"],
                credential_type=c["credential_type"],
                status=c["status"],
                issued_at=c["issued_at"],
                expires_at=c.get("expires_at"),
                claims_summary=c["claims_summary"],
            )
            for c in creds
        ]

        return ApiResponse(success=True, data=responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{wallet_address}", response_model=ApiResponse[CredentialResponse])
async def fetch_and_tokenize_credential(
    wallet_address: str, request: CredentialData
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

        cred_id = f"{wallet_address}-{request.credential_type}"
        credential = {
            "credential_id": cred_id,
            "credential_type": request.credential_type,
            "status": "active",
            "issued_at": request.fetched_at,
            "claims_summary": data,
        }

        if wallet_address not in _in_memory_store:
            _in_memory_store[wallet_address] = []
        _in_memory_store[wallet_address].append(credential)

        return ApiResponse(success=True, data=CredentialResponse(**credential))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{wallet_address}/{credential_type}", response_model=ApiResponse[CredentialResponse])
async def get_credential(wallet_address: str, credential_type: str):
    try:
        creds = _in_memory_store.get(wallet_address, [])
        cred = next((c for c in creds if c["credential_type"] == credential_type), None)

        if not cred:
            raise HTTPException(status_code=404, detail="Credential not found")

        return ApiResponse(success=True, data=CredentialResponse(**cred))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{wallet_address}/{credential_id}", response_model=ApiResponse[dict])
async def revoke_credential(wallet_address: str, credential_id: str):
    try:
        creds = _in_memory_store.get(wallet_address, [])
        cred = next((c for c in creds if c["credential_id"] == credential_id), None)

        if not cred:
            raise HTTPException(status_code=404, detail="Credential not found")

        cred["status"] = "revoked"
        cred["revocation_reason"] = "User revoked"

        return ApiResponse(success=True, data={"message": "Credential revoked"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
