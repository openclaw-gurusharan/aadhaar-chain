"""Configuration management for aadhaar-chain gateway."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "aadhaar-chain-gateway"
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Solana
    solana_rpc_url: str = "http://127.0.0.1:8899"

    # IPFS
    ipfs_gateway_url: str = "https://ipfs.io/ipfs"

    # API Setu
    apisetu_client_id: Optional[str] = None
    apisetu_client_secret: Optional[str] = None

    # Anthropic (Claude Agent SDK)
    anthropic_api_key: Optional[str] = None

    # Storage
    data_dir: str = "./data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
