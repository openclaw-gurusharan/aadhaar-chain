"""PDA (Program Derived Address) service for deriving deterministic addresses on Solana."""

from solders.pubkey import Pubkey
from config import settings
import hashlib


class PDAService:
    """Derives Program Derived Addresses matching Solana account structure."""

    # Mock program ID for testing (32 bytes)
    MOCK_PROGRAM_ID = "11111111111111111111111111111111"

    def __init__(self):
        """Initialize with program IDs from config."""
        self.identity_program_id = None
        self.credential_program_id = None

        # Load program IDs from environment
        try:
            if settings.identity_program_id and settings.identity_program_id != "idcore1111111111111111111111111111111111":
                self.identity_program_id = Pubkey.from_string(settings.identity_program_id)
        except Exception:
            pass

        try:
            if settings.credential_program_id and settings.credential_program_id != "credvault1111111111111111111111111111":
                self.credential_program_id = Pubkey.from_string(settings.credential_program_id)
        except Exception:
            pass

    @staticmethod
    def find_pda(program_id: Pubkey, seeds: list[bytes]) -> tuple[str, int]:
        """
        Find a PDA by testing bumps from 255 down to 0.

        Returns (pda_address as base58 string, bump_seed as int)
        """
        for bump in range(255, -1, -1):
            try:
                seeds_with_bump = seeds + [bytes([bump])]
                pda, _ = Pubkey.find_program_address(seeds_with_bump, program_id)
                return str(pda), bump
            except Exception:
                continue

        raise RuntimeError(f"Failed to find PDA for program {program_id} with seeds")

    @staticmethod
    def _mock_pda(seeds: list[bytes]) -> tuple[str, int]:
        """Generate a mock PDA for testing (deterministic based on seeds)."""
        # Create a deterministic hash from seeds
        seed_bytes = b"".join(seeds)
        hash_bytes = hashlib.sha256(seed_bytes).digest()[:32]

        # Convert to base58-like format (max 43 chars for Solana addresses)
        chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        result = ""
        for i, byte in enumerate(hash_bytes):
            result += chars[byte % len(chars)]

        return result[:43], 255  # Exactly 43 chars, bump=255

    def derive_identity_pda(self, wallet_address: str) -> tuple[str, int]:
        """
        Derive PDA for identity account.

        Seeds: ["identity", wallet_address]
        Returns (pda_address, bump_seed)
        """
        if not self.identity_program_id:
            # Mock mode: return deterministic mock PDA
            return self._mock_pda([b"identity", wallet_address.encode()])

        wallet_pubkey = Pubkey.from_string(wallet_address)
        seeds = [b"identity", bytes(wallet_pubkey)]

        return self.find_pda(self.identity_program_id, seeds)

    def derive_credential_pda(
        self, wallet_address: str, credential_type: str, issuer_did: str
    ) -> tuple[str, int]:
        """
        Derive PDA for credential account.

        Seeds: ["credential", wallet_address, credential_type, issuer_did]
        Returns (pda_address, bump_seed)
        """
        if not self.credential_program_id:
            # Mock mode: return deterministic mock PDA
            return self._mock_pda([
                b"credential",
                wallet_address.encode(),
                credential_type.encode("utf-8"),
                issuer_did.encode("utf-8"),
            ])

        wallet_pubkey = Pubkey.from_string(wallet_address)
        seeds = [
            b"credential",
            bytes(wallet_pubkey),
            credential_type.encode("utf-8"),
            issuer_did.encode("utf-8"),
        ]

        return self.find_pda(self.credential_program_id, seeds)

    def derive_grant_pda(
        self, credential_pda: str, grantor_wallet: str, purpose: str
    ) -> tuple[str, int]:
        """
        Derive PDA for access grant account.

        Seeds: ["grant", credential_pda, grantor_wallet, purpose]
        Returns (pda_address, bump_seed)
        """
        if not self.credential_program_id:
            raise ValueError("CREDENTIAL_PROGRAM_ID not configured")

        credential_pubkey = Pubkey.from_string(credential_pda)
        grantor_pubkey = Pubkey.from_string(grantor_wallet)
        seeds = [
            b"grant",
            bytes(credential_pubkey),
            bytes(grantor_pubkey),
            purpose.encode("utf-8"),
        ]

        return self.find_pda(self.credential_program_id, seeds)


# Singleton instance for dependency injection
pda_service = PDAService()
