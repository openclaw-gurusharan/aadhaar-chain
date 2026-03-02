"""Routes for user profile operations."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models import (
    UserProfile,
    CreateUserRequest,
    UpdateUserRequest,
    ApiResponse,
)


# In-memory store (for development)
users: dict[str, UserProfile] = {}


router = APIRouter(prefix="/api/users", tags=["users"])


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


@router.get("", response_model=ApiResponse, tags=["users"])
async def get_users():
    """Get all users (list all profiles)."""
    return ApiResponse(
        success=True,
        message="Users retrieved",
        data={
            "users": [user.model_dump() for user in users.values()]
        }
    )


@router.get("/{wallet_address}", response_model=ApiResponse, tags=["users"])
async def get_user(wallet_address: str):
    """Get user profile by wallet address."""
    if wallet_address not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ApiResponse(
        success=True,
        data=users[wallet_address].model_dump()
    )


@router.post("", response_model=ApiResponse, tags=["users"])
async def create_user(request: CreateUserRequest):
    """Create a new user profile."""
    if request.wallet_address in users:
        raise HTTPException(status_code=400, detail="User already exists")
    
    now = _get_timestamp()
    users[request.wallet_address] = UserProfile(
        wallet_address=request.wallet_address,
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        created_at=now,
        updated_at=now,
    )
    
    return ApiResponse(
        success=True,
        message="User created",
        data=users[request.wallet_address].model_dump()
    )


@router.put("/{wallet_address}", response_model=ApiResponse, tags=["users"])
async def update_user(wallet_address: str, request: UpdateUserRequest):
    """Update user profile."""
    if wallet_address not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users[wallet_address]
    
    if request.username is not None:
        user.username = request.username
    if request.email is not None:
        user.email = request.email
    if request.full_name is not None:
        user.full_name = request.full_name
    
    user.updated_at = _get_timestamp()
    
    return ApiResponse(
        success=True,
        message="User updated",
        data=user.model_dump()
    )


@router.delete("/{wallet_address}", response_model=ApiResponse, tags=["users"])
async def delete_user(wallet_address: str):
    """Delete user profile."""
    if wallet_address not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users[wallet_address]
    
    return ApiResponse(
        success=True,
        message="User deleted"
    )
