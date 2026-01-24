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
    # Supports both standard API key and z.ai GLM 4.7 proxy
    anthropic_api_key: str | None = None
    anthropic_auth_token: str | None = None
    anthropic_base_url: str | None = None

    # GLM 4.7 model overrides (optional, for z.ai proxy)
    anthropic_default_haiku_model: str | None = None
    anthropic_default_sonnet_model: str | None = None
    anthropic_default_opus_model: str | None = None

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

    # SSO / Session
    # Set IS_LOCALHOST=true for local development, false for production
    is_localhost: bool = True  # Single switch for local vs production
    session_secret: str = "change-this-in-production"
    session_duration_days: int = 30
    cookie_domain: str = ".aadharcha.in"  # Production (ignored when is_localhost=true)
    sso_allowed_origins: list[str] = [
        "http://localhost:3000",  # identity-aadhar (local dev only)
        "http://localhost:3001",  # FlatWatch (local dev)
        "http://localhost:3002",  # ONDC Buyer (local dev)
        "http://localhost:3003",  # ONDC Seller (local dev)
        "http://localhost:3004",  # ONDC Buyer (local dev)
        # Production - HTTPS only (no http versions)
        "https://aadharcha.in",
        "https://www.aadharcha.in",
        "https://flatwatch.aadharcha.in",
        "https://ondcbuyer.aadharcha.in",
        "https://ondcseller.aadharcha.in",
    ]


settings = Settings()
