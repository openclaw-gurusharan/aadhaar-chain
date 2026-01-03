import base64
from typing import Optional
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash as SolderHash
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from config import settings

# Type alias for compatibility
PublicKey = Pubkey


class SolanaService:
    def __init__(self):
        self.client = AsyncClient(settings.solana_rpc_url)
        self.identity_program_id = settings.identity_program_id
        self.credential_program_id = settings.credential_program_id

    async def close(self):
        await self.client.close()

    async def get_balance(self, wallet_address: str) -> int:
        pubkey = PublicKey.from_string(wallet_address)
        response = await self.client.get_balance(pubkey, commitment=Confirmed)
        return response.value if response.value else 0

    async def get_account_info(self, account_address: str):
        pubkey = PublicKey.from_string(account_address)
        response = await self.client.get_account_info(pubkey, commitment=Confirmed)
        return response.value

    async def get_latest_blockhash(self) -> tuple[str, int]:
        response = await self.client.get_latest_blockhash(Confirmed)
        blockhash = response.value.blockhash
        last_valid_block_height = response.value.last_valid_block_height
        return str(blockhash), last_valid_block_height

    @staticmethod
    def derive_identity_pda(wallet: str, program_id: Optional[str] = None) -> tuple[str, int]:
        wallet_pubkey = Pubkey.from_string(wallet)
        program = (
            Pubkey.from_string(program_id)
            if program_id
            else Pubkey.from_string(settings.identity_program_id)
        )
        pda, bump = Pubkey.find_program_address([b"identity", bytes(wallet_pubkey)], program)
        return str(pda), bump

    @staticmethod
    def derive_credential_pda(
        wallet: str, credential_type: str, program_id: Optional[str] = None
    ) -> tuple[str, int]:
        wallet_pubkey = Pubkey.from_string(wallet)
        cred_type_bytes = credential_type.encode().ljust(32, b"\x00")
        program = (
            Pubkey.from_string(program_id)
            if program_id
            else Pubkey.from_string(settings.credential_program_id)
        )
        pda, bump = Pubkey.find_program_address(
            [b"credential", bytes(wallet_pubkey), cred_type_bytes], program
        )
        return str(pda), bump

    async def prepare_transaction(
        self,
        instructions: list[Instruction],
        payer: str,
    ) -> dict:
        blockhash_str, last_valid_block_height = await self.get_latest_blockhash()
        blockhash = SolderHash.from_string(blockhash_str)
        payer_pubkey = Pubkey.from_string(payer)

        message = MessageV0.try_compile(
            payer=payer_pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash,
        )

        tx = VersionedTransaction(message)
        tx_base64 = base64.b64encode(bytes(tx)).decode()

        return {
            "transaction": tx_base64,
            "blockhash": blockhash_str,
            "last_valid_block_height": last_valid_block_height,
        }

    async def submit_transaction(self, signed_tx_base64: str) -> dict:
        tx_bytes = base64.b64decode(signed_tx_base64)
        tx = VersionedTransaction.from_bytes(tx_bytes)

        response = await self.client.send_transaction(tx, opts=Confirmed)
        signature = str(response.value)

        await self.client.confirm_transaction(
            response.value, commitment=Confirmed
        )

        return {"signature": signature}

    async def get_identity_account(self, wallet: str) -> Optional[dict]:
        pda, _ = self.derive_identity_pda(wallet)
        account_info = await self.get_account_info(pda)

        if account_info and account_info.data:
            return {
                "address": pda,
                "data": account_info.data,
                "owner": str(account_info.owner),
                "lamports": account_info.lamports,
            }
        return None


solana_service = SolanaService()
