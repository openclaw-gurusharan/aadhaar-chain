"""Session service for SSO cookie-based authentication."""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from db_models import Session, ConnectedApp, Identity


SESSION_COOKIE_NAME = "aadharcha_session"
SESSION_DURATION = timedelta(days=settings.session_duration_days)


def create_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(32)


async def create_session(
    db: AsyncSession,
    user_id: str,
    auth_method: str = "wallet",
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> str:
    """Create a new session for the user."""
    session_token = create_session_token()
    expires_at = datetime.utcnow() + SESSION_DURATION

    session = Session(
        user_id=user_id,
        session_token=session_token,
        auth_method=auth_method,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at,
    )
    db.add(session)
    await db.flush()

    return session_token


def set_session_cookie(response: Response, session_token: str) -> Response:
    """Set the SSO session cookie on the response.

    For localhost (is_localhost=true): domain=None, secure=False
    For production (is_localhost=false): domain=.aadharcha.in, secure=True
    """
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        domain=None if settings.is_localhost else settings.cookie_domain,
        secure=not settings.is_localhost,
        httponly=True,
        samesite="lax",
        max_age=int(SESSION_DURATION.total_seconds()),
    )
    return response


def clear_session_cookie(response: Response) -> Response:
    """Clear the SSO session cookie."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        domain=None if settings.is_localhost else settings.cookie_domain,
    )
    return response


async def validate_session(db: AsyncSession, session_token: str) -> Optional[str]:
    """
    Validate a session token and return the user_id.

    Returns None if session is invalid, expired, or revoked.
    Updates last_active on successful validation.
    """
    result = await db.execute(
        select(Session).where(
            Session.session_token == session_token,
            Session.is_revoked == False,
            Session.expires_at > datetime.utcnow(),
        )
    )
    session = result.scalar_one_or_none()

    if session:
        # Update last_active timestamp
        session.last_active = datetime.utcnow()
        await db.flush()
        return session.user_id

    return None


async def revoke_session(db: AsyncSession, session_token: str) -> bool:
    """Revoke a session by its token."""
    result = await db.execute(
        select(Session).where(Session.session_token == session_token)
    )
    session = result.scalar_one_or_none()

    if session:
        session.is_revoked = True
        await db.flush()
        return True
    return False


async def revoke_all_user_sessions(db: AsyncSession, user_id: str) -> int:
    """Revoke all sessions for a user. Returns count of revoked sessions."""
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.is_revoked == False,
        )
    )
    sessions = result.scalars().all()

    count = 0
    for session in sessions:
        session.is_revoked = True
        count += 1

    await db.flush()
    return count


async def get_user_sessions(db: AsyncSession, user_id: str) -> list[Session]:
    """Get all active sessions for a user."""
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.is_revoked == False,
            Session.expires_at > datetime.utcnow(),
        ).order_by(Session.last_active.desc())
    )
    return list(result.scalars().all())


async def record_app_access(db: AsyncSession, user_id: str, app_name: str) -> None:
    """Record or update access to a connected app."""
    # Check if app already connected
    result = await db.execute(
        select(ConnectedApp).where(
            ConnectedApp.user_id == user_id,
            ConnectedApp.app_name == app_name,
        )
    )
    connected_app = result.scalar_one_or_none()

    if connected_app:
        # Update last_accessed
        connected_app.last_accessed = datetime.utcnow()
    else:
        # Create new connected app record
        connected_app = ConnectedApp(
            user_id=user_id,
            app_name=app_name,
        )
        db.add(connected_app)

    await db.flush()


async def get_connected_apps(db: AsyncSession, user_id: str) -> list[ConnectedApp]:
    """Get all connected apps for a user, ordered by last access."""
    result = await db.execute(
        select(ConnectedApp).where(
            ConnectedApp.user_id == user_id,
        ).order_by(ConnectedApp.last_accessed.desc())
    )
    return list(result.scalars().all())
