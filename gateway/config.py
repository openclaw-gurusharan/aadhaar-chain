from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/identity_db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Anthropic / Claude Agent SDK
    anthropic_api_key: str

    # Solana
    solana_rpc_url: str = "https://api.devnet.solana.com"
    identity_program_id: str | None = None
    credential_program_id: str | None = None

    # API Setu
    apisetu_client_id: str
    apisetu_client_secret: str
    apisetu_env: str = "sandbox"

    # IPFS
    ipfs_gateway_url: str = "https://ipfs.io/ipfs"

    # Mock Mode (for testing without real API Setu)
    mock_mode: bool = True


settings = Settings()
