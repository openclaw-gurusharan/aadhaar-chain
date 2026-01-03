"""Access grant repository for database operations on AccessGrant model."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db_models import AccessGrant


class GrantRepository:
    """CRUD operations for Access Grant accounts."""

    def __init__(self, session: AsyncSession):
        """Initialize with async database session."""
        self.session = session

    async def create(
        self,
        grant_id: str,
        pda_address: str,
        credential_pda: str,
        grantor_wallet: str,
        grantee_wallet: str,
        expires_at: datetime,
        bump: int,
        purpose: Optional[str] = None,
        field_mask: int = 0,
    ) -> AccessGrant:
        """
        Create a new access grant.

        Returns the created AccessGrant object.
        """
        grant = AccessGrant(
            grant_id=grant_id,
            pda_address=pda_address,
            credential_pda=credential_pda,
            grantor_wallet=grantor_wallet,
            grantee_wallet=grantee_wallet,
            expires_at=expires_at,
            bump=bump,
            purpose=purpose,
            field_mask=field_mask,
        )
        self.session.add(grant)
        await self.session.flush()
        return grant

    async def get(self, grant_id: str) -> Optional[AccessGrant]:
        """Get grant by grant_id."""
        stmt = select(AccessGrant).where(AccessGrant.grant_id == grant_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_pda(self, pda_address: str) -> Optional[AccessGrant]:
        """Get grant by PDA address."""
        stmt = select(AccessGrant).where(AccessGrant.pda_address == pda_address)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_credential(
        self, credential_pda: str, include_revoked: bool = False
    ) -> List[AccessGrant]:
        """List grants for a specific credential."""
        query = select(AccessGrant).where(AccessGrant.credential_pda == credential_pda)

        if not include_revoked:
            query = query.where(AccessGrant.revoked == False)

        query = query.order_by(AccessGrant.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_grantor(
        self, grantor_wallet: str, include_revoked: bool = False
    ) -> List[AccessGrant]:
        """List grants granted by a specific wallet."""
        query = select(AccessGrant).where(AccessGrant.grantor_wallet == grantor_wallet)

        if not include_revoked:
            query = query.where(AccessGrant.revoked == False)

        query = query.order_by(AccessGrant.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_grantee(
        self, grantee_wallet: str, include_revoked: bool = False
    ) -> List[AccessGrant]:
        """List grants granted to a specific wallet."""
        query = select(AccessGrant).where(AccessGrant.grantee_wallet == grantee_wallet)

        if not include_revoked:
            query = query.where(AccessGrant.revoked == False)

        query = query.order_by(AccessGrant.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_active(self) -> List[AccessGrant]:
        """List all active (not revoked and not expired) grants."""
        now = datetime.utcnow()
        stmt = (
            select(AccessGrant)
            .where(
                (AccessGrant.revoked == False)
                & (AccessGrant.expires_at > now)
            )
            .order_by(AccessGrant.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_expired(self) -> List[AccessGrant]:
        """List all expired grants."""
        now = datetime.utcnow()
        stmt = (
            select(AccessGrant)
            .where(AccessGrant.expires_at < now)
            .order_by(AccessGrant.expires_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_field_mask(
        self, grant_id: str, field_mask: int
    ) -> Optional[AccessGrant]:
        """Update the field mask for selective disclosure."""
        stmt = (
            update(AccessGrant)
            .where(AccessGrant.grant_id == grant_id)
            .values(field_mask=field_mask)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(grant_id)

    async def revoke(self, grant_id: str) -> Optional[AccessGrant]:
        """Revoke an access grant."""
        stmt = (
            update(AccessGrant)
            .where(AccessGrant.grant_id == grant_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(grant_id)

    async def unrevoke(self, grant_id: str) -> Optional[AccessGrant]:
        """Unrevoke an access grant."""
        stmt = (
            update(AccessGrant)
            .where(AccessGrant.grant_id == grant_id)
            .values(revoked=False)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(grant_id)

    async def delete(self, grant_id: str) -> bool:
        """
        Delete an access grant.

        Returns True if deleted, False if not found.
        """
        grant = await self.get(grant_id)
        if not grant:
            return False

        await self.session.delete(grant)
        await self.session.flush()
        return True
