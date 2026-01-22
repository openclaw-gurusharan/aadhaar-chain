"""SSO authentication routes for cookie-based cross-subdomain login."""
from fastapi import APIRouter, HTTPException, Response, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from db_models import Identity
from repositories.identity_repo import IdentityRepository
from services.session import (
    create_session,
    set_session_cookie,
    clear_session_cookie,
    validate_session,
    revoke_session,
    get_user_sessions,
    record_app_access,
    get_connected_apps,
    SESSION_COOKIE_NAME,
)
from models.auth import (
    LoginRequest,
    LoginResponse,
    SessionInfo,
    UserResponse,
    ValidateResponse,
    ConnectedAppsResponse,
    ConnectedAppInfo,
    SessionsResponse,
)
from models.common import ApiResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])

# Display names for connected apps
APP_DISPLAY_NAMES = {
    "flatwatch": "FlatWatch",
    "ondc_buyer": "ONDC Buyer Portal",
    "ondc_seller": "ONDC Seller Portal",
    "identity_aadhar": "Identity Aadhaar",
}


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with wallet address and create SSO session.

    Sets a domain-wide cookie that works across all *.aadharcha.in subdomains.
    """
    try:
        # Get or create identity
        repo = IdentityRepository(db)
        identity = await repo.get(login_data.wallet_address)

        if not identity:
            # Auto-create identity for login (simplified flow)
            from services.pda import PDAService
            pda_service = PDAService()
            pda, bump = pda_service.derive_identity_pda(login_data.wallet_address)

            identity = await repo.create(
                wallet_address=login_data.wallet_address,
                pda_address=pda,
                owner_pubkey=login_data.wallet_address,
                bump=bump,
                commitment_hash=None,
                metadata_uri=None,
            )
            await db.flush()

        # Create session
        user_agent = request.headers.get("user-agent")
        client_ip = request.client.host if request.client else None

        session_token = await create_session(
            db=db,
            user_id=identity.wallet_address,
            auth_method="wallet",
            user_agent=user_agent,
            ip_address=client_ip,
        )

        # Get the created session
        from db_models import Session as SessionModel
        session_result = await db.execute(
            select(SessionModel).where(SessionModel.session_token == session_token)
        )
        session = session_result.scalar_one()

        # Commit transaction
        await db.commit()

        # Set SSO cookie
        set_session_cookie(response, session_token)

        # Record app access (identity_aadhar)
        await record_app_access(db, identity.wallet_address, "identity_aadhar")
        await db.commit()

        return ApiResponse(
            success=True,
            data=LoginResponse(
                user=UserResponse(
                    wallet_address=identity.wallet_address,
                    pda_address=identity.pda_address,
                    owner_pubkey=identity.owner_pubkey,
                    created_at=int(identity.created_at.timestamp()),
                ),
                session=SessionInfo(
                    session_id=session.id,
                    created_at=int(session.created_at.timestamp()),
                    last_active=int(session.last_active.timestamp()),
                    expires_at=int(session.expires_at.timestamp()),
                    user_agent=session.user_agent,
                    ip_address=session.ip_address,
                ),
            ),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout by revoking the current session and clearing the cookie.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if session_token:
            # Revoke session in database
            await revoke_session(db, session_token)
            await db.commit()

        # Clear cookie
        clear_session_cookie(response)

        return ApiResponse(success=True, data={"message": "Logged out successfully"})
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate", response_model=ApiResponse[ValidateResponse])
async def validate(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate session for child apps.

    Called by child apps (FlatWatch, ONDC Buyer/Seller) to validate
    the SSO cookie and get user information.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_token:
            return ApiResponse(
                success=True,
                data=ValidateResponse(valid=False, user=None),
            )

        # Validate session
        user_id = await validate_session(db, session_token)

        if not user_id:
            return ApiResponse(
                success=True,
                data=ValidateResponse(valid=False, user=None),
            )

        # Get user data
        repo = IdentityRepository(db)
        identity = await repo.get(user_id)

        if not identity:
            return ApiResponse(
                success=True,
                data=ValidateResponse(valid=False, user=None),
            )

        await db.commit()

        return ApiResponse(
            success=True,
            data=ValidateResponse(
                valid=True,
                user=UserResponse(
                    wallet_address=identity.wallet_address,
                    pda_address=identity.pda_address,
                    owner_pubkey=identity.owner_pubkey,
                    created_at=int(identity.created_at.timestamp()),
                ),
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user from SSO cookie.

    Similar to /validate but returns user directly for simpler client usage.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_token:
            raise HTTPException(status_code=401, detail="No session cookie")

        # Validate session
        user_id = await validate_session(db, session_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        # Get user data
        repo = IdentityRepository(db)
        identity = await repo.get(user_id)

        if not identity:
            raise HTTPException(status_code=404, detail="User not found")

        await db.commit()

        return ApiResponse(
            success=True,
            data=UserResponse(
                wallet_address=identity.wallet_address,
                pda_address=identity.pda_address,
                owner_pubkey=identity.owner_pubkey,
                created_at=int(identity.created_at.timestamp()),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=ApiResponse[SessionsResponse])
async def list_sessions(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    List all active sessions for the current user.

    For dashboard UI showing active devices/sessions.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_token:
            raise HTTPException(status_code=401, detail="No session cookie")

        user_id = await validate_session(db, session_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Get all user sessions
        sessions = await get_user_sessions(db, user_id)

        await db.commit()

        return ApiResponse(
            success=True,
            data=SessionsResponse(
                sessions=[
                    SessionInfo(
                        session_id=s.id,
                        created_at=int(s.created_at.timestamp()),
                        last_active=int(s.last_active.timestamp()),
                        expires_at=int(s.expires_at.timestamp()),
                        user_agent=s.user_agent,
                        ip_address=s.ip_address,
                    )
                    for s in sessions
                ]
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/revoke", response_model=ApiResponse[dict])
async def revoke_session_endpoint(
    session_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session.

    For dashboard UI "revoke session" button.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_token:
            raise HTTPException(status_code=401, detail="No session cookie")

        user_id = await validate_session(db, session_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Find and revoke the session
        from db_models import Session as SessionModel
        from sqlalchemy import and_

        result = await db.execute(
            select(SessionModel).where(
                and_(
                    SessionModel.id == session_id,
                    SessionModel.user_id == user_id,
                )
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.is_revoked = True
        await db.commit()

        return ApiResponse(success=True, data={"message": "Session revoked"})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apps", response_model=ApiResponse[ConnectedAppsResponse])
async def list_connected_apps(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    List all connected apps for the current user.

    For dashboard UI showing connected apps with last access time.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_token:
            raise HTTPException(status_code=401, detail="No session cookie")

        user_id = await validate_session(db, session_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Get connected apps
        apps = await get_connected_apps(db, user_id)

        await db.commit()

        return ApiResponse(
            success=True,
            data=ConnectedAppsResponse(
                apps=[
                    ConnectedAppInfo(
                        app_name=app.app_name,
                        display_name=APP_DISPLAY_NAMES.get(
                            app.app_name, app.app_name.title()
                        ),
                        first_accessed=int(app.first_accessed.timestamp()),
                        last_accessed=int(app.last_accessed.timestamp()),
                    )
                    for app in apps
                ]
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apps/{app_name}/access", response_model=ApiResponse[dict])
async def record_app_access_endpoint(
    app_name: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Record access to a connected app.

    Called by child apps on first access to track user's app usage.
    """
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if not session_token:
            raise HTTPException(status_code=401, detail="No session cookie")

        user_id = await validate_session(db, session_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Record app access
        await record_app_access(db, user_id, app_name)
        await db.commit()

        return ApiResponse(success=True, data={"message": "App access recorded"})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
