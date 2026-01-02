from pydantic import BaseModel, Field
from typing import Optional, Literal, Any
from datetime import datetime


class AadhaarData(BaseModel):
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    name: str
    dob: str
    gender: str
    address: str
    pincode: str


class PANData(BaseModel):
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    name: str
    father_name: str
    dob: str
    pan_status: str


class DrivingLicenseData(BaseModel):
    dl_number: str
    name: str
    dob: str
    address: str
    issue_date: str
    expiry_date: str
    vehicle_classes: list[str]


class LandRecordData(BaseModel):
    property_id: str
    owner_name: str
    property_address: str
    area: str
    survey_number: str
    ownership_type: str


class EducationData(BaseModel):
    degree: str
    university: str
    year: int
    roll_number: str
    student_name: str
    specialization: Optional[str] = None


class CredentialData(BaseModel):
    credential_type: Literal["aadhaar", "pan", "dl", "land", "education"]
    data: AadhaarData | PANData | DrivingLicenseData | LandRecordData | EducationData
    source: str = Field(default="apisetu")
    fetched_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))


class CredentialToken(BaseModel):
    credential_id: str
    credential_type: str
    owner: str
    claims: dict[str, Any]
    metadata: dict[str, Any]
    issued_at: int
    expiry: Optional[int] = None
    revocation_reason: Optional[str] = None


class AccessGrant(BaseModel):
    grant_id: str
    credential_id: str
    granted_to: str = Field(..., description="Service identifier or DID")
    fields: list[str] = Field(..., description="Selective disclosure fields")
    purpose: str
    expires_at: int
    created_at: int
    revoked_at: Optional[int] = None


class CredentialResponse(BaseModel):
    credential_id: str
    credential_type: str
    status: Literal["active", "expired", "revoked"]
    issued_at: int
    expires_at: Optional[int]
    claims_summary: dict[str, Any]
