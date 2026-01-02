import httpx
from typing import Any
from config import settings


class APISetuClient:
    BASE_URL_SANDBOX = "https://sandbox.apisetu.com"
    BASE_URL_PRODUCTION = "https://api.apisetu.com"

    def __init__(self):
        self.base_url = (
            self.BASE_URL_PRODUCTION
            if settings.apisetu_env == "production"
            else self.BASE_URL_SANDBOX
        )
        self.client_id = settings.apisetu_client_id
        self.client_secret = settings.apisetu_client_secret

    async def _request(
        self, method: str, endpoint: str, json_data: dict | None = None
    ) -> dict:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-APISETU-CLIENTID": self.client_id,
            "X-APISETU-CLIENTSECRET": self.client_secret,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=json_data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    async def fetch_aadhaar(
        self, aadhaar_number: str, otp: str | None = None
    ) -> dict[str, Any]:
        endpoint = "/aadhaar/v2/fetch"
        payload = {"aadhaar_number": aadhaar_number}
        if otp:
            payload["otp"] = otp

        response = await self._request("POST", endpoint, payload)
        return self._parse_aadhaar_response(response)

    async def fetch_pan(self, pan_number: str) -> dict[str, Any]:
        endpoint = "/pan/v2/fetch"
        payload = {"pan_number": pan_number}

        response = await self._request("POST", endpoint, payload)
        return self._parse_pan_response(response)

    async def fetch_driving_license(self, dl_number: str, dob: str) -> dict[str, Any]:
        endpoint = "/dl/v2/fetch"
        payload = {"dl_number": dl_number, "dob": dob}

        response = await self._request("POST", endpoint, payload)
        return self._parse_dl_response(response)

    async def fetch_land_records(
        self, state: str, district: str, survey_number: str
    ) -> dict[str, Any]:
        endpoint = "/land/v2/fetch"
        payload = {
            "state": state,
            "district": district,
            "survey_number": survey_number,
        }

        response = await self._request("POST", endpoint, payload)
        return self._parse_land_response(response)

    async def fetch_education(
        self, roll_number: str, year: int, board: str
    ) -> dict[str, Any]:
        endpoint = "/education/v2/fetch"
        payload = {
            "roll_number": roll_number,
            "year": year,
            "board": board,
        }

        response = await self._request("POST", endpoint, payload)
        return self._parse_education_response(response)

    @staticmethod
    def _parse_aadhaar_response(response: dict) -> dict:
        data = response.get("data", {})
        return {
            "credential_type": "aadhaar",
            "aadhaar_number": data.get("aadhaar_number", "")[-4:],
            "name": data.get("name"),
            "dob": data.get("date_of_birth"),
            "gender": data.get("gender"),
            "address": data.get("address", {}).get("full_address"),
            "pincode": data.get("address", {}).get("pincode"),
        }

    @staticmethod
    def _parse_pan_response(response: dict) -> dict:
        data = response.get("data", {})
        return {
            "credential_type": "pan",
            "pan_number": data.get("pan_number"),
            "name": data.get("name"),
            "father_name": data.get("father_name"),
            "dob": data.get("date_of_birth"),
            "pan_status": data.get("pan_status"),
        }

    @staticmethod
    def _parse_dl_response(response: dict) -> dict:
        data = response.get("data", {})
        return {
            "credential_type": "dl",
            "dl_number": data.get("dl_number"),
            "name": data.get("name"),
            "dob": data.get("date_of_birth"),
            "address": data.get("address"),
            "issue_date": data.get("issue_date"),
            "expiry_date": data.get("expiry_date"),
            "vehicle_classes": data.get("vehicle_classes", []),
        }

    @staticmethod
    def _parse_land_response(response: dict) -> dict:
        data = response.get("data", {})
        return {
            "credential_type": "land",
            "property_id": data.get("property_id"),
            "owner_name": data.get("owner_name"),
            "property_address": data.get("property_address"),
            "area": data.get("area"),
            "survey_number": data.get("survey_number"),
            "ownership_type": data.get("ownership_type"),
        }

    @staticmethod
    def _parse_education_response(response: dict) -> dict:
        data = response.get("data", {})
        return {
            "credential_type": "education",
            "degree": data.get("degree"),
            "university": data.get("university"),
            "year": data.get("year"),
            "roll_number": data.get("roll_number"),
            "student_name": data.get("student_name"),
            "specialization": data.get("specialization"),
        }


apisetu_client = APISetuClient()
