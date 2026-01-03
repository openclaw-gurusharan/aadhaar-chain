"""Credential repository for database operations on Credential model."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db_models import Credential


class CredentialRepository:
    """CRUD operations for Credential accounts."""

    def __init__(self, session: AsyncSession):
        """Initialize with async database session."""
        self.session = session

    async def create(
        self,
        credential_id: str,
        pda_address: str,
        owner_wallet: str,
        credential_type: str,
        claims_hash: bytes,
        issued_at: datetime,
        bump: int,
        issuer_did: Optional[str] = None,
        expiry: Optional[datetime] = None,
        metadata_uri: Optional[str] = None,
    ) -> Credential:
        """
        Create a new credential account.

        Returns the created Credential object.
        """
        credential = Credential(
            credential_id=credential_id,
            pda_address=pda_address,
            owner_wallet=owner_wallet,
            credential_type=credential_type,
            claims_hash=claims_hash,
            issued_at=issued_at,
            bump=bump,
            issuer_did=issuer_did,
            expiry=expiry,
            metadata_uri=metadata_uri,
        )
        self.session.add(credential)
        await self.session.flush()
        return credential

    async def get(self, credential_id: str) -> Optional[Credential]:
        """Get credential by credential_id."""
        stmt = select(Credential).where(Credential.credential_id == credential_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_pda(self, pda_address: str) -> Optional[Credential]:
        """Get credential by PDA address."""
        stmt = select(Credential).where(Credential.pda_address == pda_address)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_owner(self, owner_wallet: str) -> List[Credential]:
        """List all credentials for a wallet owner."""
        stmt = (
            select(Credential)
            .where(Credential.owner_wallet == owner_wallet)
            .order_by(Credential.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_type(
        self, owner_wallet: str, credential_type: str
    ) -> List[Credential]:
        """List credentials of specific type for a wallet owner."""
        stmt = (
            select(Credential)
            .where(
                (Credential.owner_wallet == owner_wallet)
                & (Credential.credential_type == credential_type)
            )
            .order_by(Credential.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_active(self, owner_wallet: str) -> List[Credential]:
        """List non-revoked credentials for a wallet owner."""
        stmt = (
            select(Credential)
            .where(
                (Credential.owner_wallet == owner_wallet) & (Credential.revoked == False)
            )
            .order_by(Credential.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_expired(self) -> List[Credential]:
        """List all expired credentials across all users."""
        stmt = (
            select(Credential)
            .where(
                (Credential.expiry.isnot(None)) & (Credential.expiry < datetime.utcnow())
            )
            .order_by(Credential.expiry.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_metadata(
        self, credential_id: str, metadata_uri: str
    ) -> Optional[Credential]:
        """Update credential metadata URI."""
        stmt = (
            update(Credential)
            .where(Credential.credential_id == credential_id)
            .values(metadata_uri=metadata_uri)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(credential_id)

    async def revoke(self, credential_id: str) -> Optional[Credential]:
        """Mark credential as revoked."""
        stmt = (
            update(Credential)
            .where(Credential.credential_id == credential_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(credential_id)

    async def unrevoke(self, credential_id: str) -> Optional[Credential]:
        """Unrevoke a credential."""
        stmt = (
            update(Credential)
            .where(Credential.credential_id == credential_id)
            .values(revoked=False)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(credential_id)

    async def delete(self, credential_id: str) -> bool:
        """
        Delete a credential account (cascades to access grants).

        Returns True if deleted, False if not found.
        """
        credential = await self.get(credential_id)
        if not credential:
            return False

        await self.session.delete(credential)
        await self.session.flush()
        return True
