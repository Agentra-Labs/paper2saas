"""Shared pytest fixtures for Paper2SaaS tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_s2_config():
    """Create a test S2Config with default values."""
    from paper2saas.tools.s2_config import S2Config

    return S2Config(
        api_key=None,
        requests_per_second=100.0,
        search_rate_limit=100.0,
        cache_ttl=60,
        cache_maxsize=10,
    )


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""
    return {
        "paperId": "test123",
        "title": "Test Paper",
        "year": 2024,
        "authors": [{"name": "Test Author"}],
        "abstract": "This is a test abstract.",
        "citationCount": 42,
    }


@pytest.fixture
def mock_search_response():
    """Create a mock search response."""
    return {
        "data": [
            {
                "paperId": "paper1",
                "title": "First Paper",
                "year": 2023,
                "authors": [{"name": "Author One"}],
                "citationCount": 100,
            },
            {
                "paperId": "paper2",
                "title": "Second Paper",
                "year": 2024,
                "authors": [{"name": "Author Two"}],
                "citationCount": 50,
            },
        ]
    }


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx AsyncClient."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    from paper2saas.config import Settings

    return Settings(
        mistral_api_key="test-key",
        small_model="test-model",
        large_model="test-model",
    )
