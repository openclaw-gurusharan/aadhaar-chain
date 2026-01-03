"""Identity repository for database operations on Identity model."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db_models import Identity


class IdentityRepository:
    """CRUD operations for Identity accounts."""

    def __init__(self, session: AsyncSession):
        """Initialize with async database session."""
        self.session = session

    async def create(
        self,
        wallet_address: str,
        pda_address: str,
        owner_pubkey: str,
        bump: int,
        commitment_hash: Optional[bytes] = None,
        metadata_uri: Optional[str] = None,
    ) -> Identity:
        """
        Create a new identity account.

        Returns the created Identity object.
        """
        identity = Identity(
            wallet_address=wallet_address,
            pda_address=pda_address,
            owner_pubkey=owner_pubkey,
            bump=bump,
            commitment_hash=commitment_hash,
            metadata_uri=metadata_uri,
        )
        self.session.add(identity)
        await self.session.flush()
        return identity

    async def get(self, wallet_address: str) -> Optional[Identity]:
        """Get identity by wallet address."""
        stmt = select(Identity).where(Identity.wallet_address == wallet_address)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_pda(self, pda_address: str) -> Optional[Identity]:
        """Get identity by PDA address."""
        stmt = select(Identity).where(Identity.pda_address == pda_address)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update(
        self,
        wallet_address: str,
        commitment_hash: Optional[bytes] = None,
        metadata_uri: Optional[str] = None,
        recovery_counter: Optional[int] = None,
    ) -> Optional[Identity]:
        """
        Update an existing identity account.

        Returns the updated Identity object.
        """
        # Build update dictionary with only provided fields
        update_dict = {}
        if commitment_hash is not None:
            update_dict["commitment_hash"] = commitment_hash
        if metadata_uri is not None:
            update_dict["metadata_uri"] = metadata_uri
        if recovery_counter is not None:
            update_dict["recovery_counter"] = recovery_counter

        if not update_dict:
            # No fields to update, return existing identity
            return await self.get(wallet_address)

        stmt = (
            update(Identity)
            .where(Identity.wallet_address == wallet_address)
            .values(**update_dict)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        # Return updated identity
        return await self.get(wallet_address)

    async def set_verification_bit(
        self, wallet_address: str, bit_position: int
    ) -> Optional[Identity]:
        """
        Set a specific bit in the verification_bits field.

        bit_position: 0-31 for a 32-bit field
        Returns the updated Identity object.
        """
        identity = await self.get(wallet_address)
        if not identity:
            return None

        # Set the bit at position
        identity.verification_bits |= 1 << bit_position

        stmt = (
            update(Identity)
            .where(Identity.wallet_address == wallet_address)
            .values(verification_bits=identity.verification_bits)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(wallet_address)

    async def unset_verification_bit(
        self, wallet_address: str, bit_position: int
    ) -> Optional[Identity]:
        """
        Unset a specific bit in the verification_bits field.

        bit_position: 0-31 for a 32-bit field
        Returns the updated Identity object.
        """
        identity = await self.get(wallet_address)
        if not identity:
            return None

        # Unset the bit at position
        identity.verification_bits &= ~(1 << bit_position)

        stmt = (
            update(Identity)
            .where(Identity.wallet_address == wallet_address)
            .values(verification_bits=identity.verification_bits)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return await self.get(wallet_address)

    async def is_verification_bit_set(
        self, wallet_address: str, bit_position: int
    ) -> bool:
        """Check if a specific verification bit is set."""
        identity = await self.get(wallet_address)
        if not identity:
            return False

        return bool(identity.verification_bits & (1 << bit_position))

    async def delete(self, wallet_address: str) -> bool:
        """
        Delete an identity account (cascades to credentials and grants).

        Returns True if deleted, False if not found.
        """
        identity = await self.get(wallet_address)
        if not identity:
            return False

        await self.session.delete(identity)
        await self.session.flush()
        return True
