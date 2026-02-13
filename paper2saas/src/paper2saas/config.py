"""Centralized configuration for Paper2SaaS.

Uses Pydantic Settings for type-safe environment variable loading.
"""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Valid log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    API keys are stored as SecretStr for secure handling.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    # LLM Configuration
    mistral_api_key: SecretStr = SecretStr("")
    openai_api_key: SecretStr = SecretStr("")
    anthropic_api_key: SecretStr = SecretStr("")

    # Model Selection
    large_model: str = "mistral:mistral-large-latest"
    small_model: str = "mistral:mistral-small-latest"
    product_engineer_model: str = ""
    validation_researcher_model: str = ""

    # Pollinations.ai (Multi-provider gateway)
    pollinations_api_key: SecretStr = SecretStr("")
    pollinations_base_url: str = "https://gen.pollinations.ai/v1"
    pollinations_model: str = "nova-fast"

    # Semantic Scholar
    s2_api_key: SecretStr = SecretStr("")
    s2_base_url: str = "https://api.semanticscholar.org/graph/v1"
    s2_recommendations_url: str = "https://api.semanticscholar.org/recommendations/v1"
    s2_requests_per_second: float = 0.33
    s2_search_rate_limit: float = 0.2
    s2_cache_ttl: int = 3600
    s2_cache_maxsize: int = 1000

    # HTTP Timeouts
    connect_timeout: float = 5.0
    read_timeout: float = 30.0

    # Reasoning Configuration
    reasoning_min_steps: int = 2
    reasoning_max_steps: int = 8

    # Database
    database_url: str = ""
    supabase_project: str = ""
    supabase_password: str = ""

    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_to_file: bool = False

    # Feature Flags
    enable_markdown: bool = True
    store_events: bool = True
    show_member_responses: bool = True

    # Optional Tools
    firecrawl_api_key: SecretStr = SecretStr("")
    baidu_search_api_key: SecretStr = SecretStr("")

    @property
    def mistral_api_key_value(self) -> str:
        """Get raw API key value."""
        return self.mistral_api_key.get_secret_value()

    @property
    def s2_api_key_value(self) -> str | None:
        """Get raw S2 API key value."""
        key = self.s2_api_key.get_secret_value()
        return key if key else None

    @property
    def pollinations_api_key_value(self) -> str | None:
        """Get raw Pollinations API key value."""
        key = self.pollinations_api_key.get_secret_value()
        return key if key else None

    def get_large_model(self) -> str:
        """Get configured large model ID."""
        return self.large_model

    def get_small_model(self) -> str:
        """Get configured small model ID."""
        return self.small_model

    def get_product_engineer_model(self) -> str:
        """Get configured product engineer model."""
        return self.product_engineer_model or self.large_model

    def get_validation_researcher_model(self) -> str:
        """Get configured validation researcher model."""
        return self.validation_researcher_model or self.small_model


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        A singleton Settings instance with environment variables loaded.
    """
    return Settings()
