"""
Anthropic client factory with GLM 4.7 proxy support.

Supports both standard Anthropic API and z.ai GLM 4.7 proxy
with automatic fallback pattern.
"""
import os
from anthropic import Anthropic, AsyncAnthropic

# Handle both direct execution and module import
try:
    from gateway.config import settings
except ImportError:
    from config import settings


def get_anthropic_client() -> Anthropic:
    """
    Get sync Anthropic client with GLM 4.7 proxy support.

    Fallback pattern:
    1. Uses ANTHROPIC_AUTH_TOKEN if available (z.ai proxy)
    2. Falls back to ANTHROPIC_API_KEY (standard Anthropic)

    Base URL:
    - Uses ANTHROPIC_BASE_URL if set (z.ai proxy)
    - Defaults to https://api.anthropic.com
    """
    api_key = settings.anthropic_auth_token or settings.anthropic_api_key

    if not api_key:
        raise ValueError(
            "Either ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY must be set. "
            "For z.ai GLM 4.7 proxy, use ANTHROPIC_AUTH_TOKEN."
        )

    base_url = settings.anthropic_base_url or "https://api.anthropic.com"

    return Anthropic(
        api_key=api_key,
        base_url=base_url,
        default_headers={"anthropic-version": "2023-06-01"},
    )


def get_async_anthropic_client() -> AsyncAnthropic:
    """
    Get async Anthropic client with GLM 4.7 proxy support.

    Same fallback pattern as get_anthropic_client().
    """
    api_key = settings.anthropic_auth_token or settings.anthropic_api_key

    if not api_key:
        raise ValueError(
            "Either ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY must be set. "
            "For z.ai GLM 4.7 proxy, use ANTHROPIC_AUTH_TOKEN."
        )

    base_url = settings.anthropic_base_url or "https://api.anthropic.com"

    return AsyncAnthropic(
        api_key=api_key,
        base_url=base_url,
        default_headers={"anthropic-version": "2023-06-01"},
    )


def get_model_override(default_model: str = "claude-3-5-sonnet-20241022") -> str:
    """
    Get model name with GLM 4.7 override if configured.

    Checks settings for model-specific overrides:
    - anthropic_default_haiku_model
    - anthropic_default_sonnet_model
    - anthropic_default_opus_model

    Args:
        default_model: Default model to use if no override configured

    Returns:
        Model name to use (either override or default)
    """
    model_lower = default_model.lower()

    if "haiku" in model_lower and settings.anthropic_default_haiku_model:
        return settings.anthropic_default_haiku_model
    if "sonnet" in model_lower and settings.anthropic_default_sonnet_model:
        return settings.anthropic_default_sonnet_model
    if "opus" in model_lower and settings.anthropic_default_opus_model:
        return settings.anthropic_default_opus_model

    return default_model


# Singleton instances for convenience
_anthropic_client: Anthropic | None = None
_async_anthropic_client: AsyncAnthropic | None = None


def get_client() -> Anthropic:
    """Get cached sync client (singleton pattern)."""
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = get_anthropic_client()
    return _anthropic_client


def get_async_client() -> AsyncAnthropic:
    """Get cached async client (singleton pattern)."""
    global _async_anthropic_client
    if _async_anthropic_client is None:
        _async_anthropic_client = get_async_anthropic_client()
    return _async_anthropic_client
