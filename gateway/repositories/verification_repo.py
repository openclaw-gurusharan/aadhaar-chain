"""Verification repository for database operations on Verification model."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db_models import Verification


class VerificationRepository:
    """CRUD operations for Verification status tracking."""

    def __init__(self, session: AsyncSession):
        """Initialize with async database session."""
        self.session = session

    async def create(
        self,
        verification_id: str,
        wallet_address: str,
        credential_type: str,
        overall_status: str = "pending",
        progress: int = 0,
    ) -> Verification:
        """
        Create a new verification record.

        Returns the created Verification object.
        """
        verification = Verification(
            verification_id=verification_id,
            wallet_address=wallet_address,
            credential_type=credential_type,
            overall_status=overall_status,
            progress=progress,
        )
        self.session.add(verification)
        await self.session.flush()
        return verification

    async def get(self, verification_id: str) -> Optional[Verification]:
        """Get verification by verification_id."""
        stmt = select(Verification).where(
            Verification.verification_id == verification_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_wallet_and_type(
        self, wallet_address: str, credential_type: str
    ) -> Optional[Verification]:
        """Get latest verification for wallet and credential type."""
        stmt = (
            select(Verification)
            .where(
                (Verification.wallet_address == wallet_address)
                & (Verification.credential_type == credential_type)
            )
            .order_by(Verification.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_wallet(self, wallet_address: str) -> List[Verification]:
        """List all verifications for a wallet."""
        stmt = (
            select(Verification)
            .where(Verification.wallet_address == wallet_address)
            .order_by(Verification.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_pending(self) -> List[Verification]:
        """List all pending verifications."""
        stmt = (
            select(Verification)
            .where(Verification.overall_status.in_(["pending", "in_progress"]))
            .order_by(Verification.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_status(self, status: str) -> List[Verification]:
        """List all verifications with specific status."""
        stmt = (
            select(Verification)
            .where(Verification.overall_status == status)
            .order_by(Verification.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self, verification_id: str, overall_status: str, progress: int = None
    ) -> Optional[Verification]:
        """
        Update verification status and progress.

        overall_status: "pending", "in_progress", "verified", "failed", "expired"
        progress: 0-100 percentage
        """
        update_dict = {"overall_status": overall_status}
        if progress is not None:
            update_dict["progress"] = progress

        stmt = (
            update(Verification)
            .where(Verification.verification_id == verification_id)
            .values(**update_dict)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(verification_id)

    async def update_step_status(
        self,
        verification_id: str,
        step_name: str,
        step_status: str,
    ) -> Optional[Verification]:
        """
        Update the status of a specific verification step.

        step_name: e.g., "api_setu_fetch", "document_validation", etc.
        step_status: "pending", "success", "failed"
        """
        verification = await self.get(verification_id)
        if not verification:
            return None

        # Update the step in the JSON field
        verification.steps[step_name] = step_status

        stmt = (
            update(Verification)
            .where(Verification.verification_id == verification_id)
            .values(steps=verification.steps)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(verification_id)

    async def set_error(
        self, verification_id: str, error_message: str
    ) -> Optional[Verification]:
        """Set error message and mark status as failed."""
        stmt = (
            update(Verification)
            .where(Verification.verification_id == verification_id)
            .values(
                overall_status="failed",
                error_message=error_message,
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(verification_id)

    async def mark_completed(
        self, verification_id: str, status: str = "verified"
    ) -> Optional[Verification]:
        """Mark verification as completed with final status."""
        stmt = (
            update(Verification)
            .where(Verification.verification_id == verification_id)
            .values(
                overall_status=status,
                progress=100,
                completed_at=datetime.utcnow(),
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(verification_id)

    async def delete(self, verification_id: str) -> bool:
        """
        Delete a verification record.

        Returns True if deleted, False if not found.
        """
        verification = await self.get(verification_id)
        if not verification:
            return False

        await self.session.delete(verification)
        await self.session.flush()
        return True
