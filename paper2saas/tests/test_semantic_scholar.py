"""Tests for Semantic Scholar tools and HTTP client"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestS2Config:
    """Tests for S2Config dataclass"""
    
    def test_default_values(self):
        """S2Config should have sensible defaults."""
        from paper2saas.tools.s2_config import S2Config
        
        config = S2Config()
        
        assert config.base_url == "https://api.semanticscholar.org/graph/v1"
        assert config.requests_per_second == 0.33
        assert config.cache_ttl == 3600
        assert config.batch_size == 500
    
    def test_custom_values(self):
        """S2Config should accept custom values."""
        from paper2saas.tools.s2_config import S2Config
        
        config = S2Config(
            api_key="test_key",
            requests_per_second=100.0,
            cache_ttl=7200,
        )
        
        assert config.api_key == "test_key"
        assert config.requests_per_second == 100.0
        assert config.cache_ttl == 7200


class TestRateLimiter:
    """Tests for RateLimiter"""
    
    @pytest.mark.asyncio
    async def test_acquire_consumes_token(self):
        """Acquire should consume a token."""
        from paper2saas.tools.http_client import RateLimiter
        
        limiter = RateLimiter(rate=10.0, per=1.0)
        initial_tokens = limiter.tokens
        
        await limiter.acquire()
        
        assert limiter.tokens < initial_tokens
    
    @pytest.mark.asyncio
    async def test_acquire_multiple(self):
        """Multiple acquires should work without blocking if tokens available."""
        from paper2saas.tools.http_client import RateLimiter
        
        limiter = RateLimiter(rate=100.0, per=1.0)
        
        # Should complete quickly without blocking
        for _ in range(5):
            await limiter.acquire()
        
        assert limiter.tokens >= 0


class TestSemanticScholarTools:
    """Tests for SemanticScholarTools toolkit"""
    
    def test_initialization(self, mock_s2_config):
        """SemanticScholarTools should initialize with config."""
        from paper2saas.tools import SemanticScholarTools
        
        tools = SemanticScholarTools(config=mock_s2_config)
        
        assert tools.config == mock_s2_config
        assert tools.name == "semantic_scholar"
    
    def test_has_sync_methods(self):
        """SemanticScholarTools should have sync wrapper methods."""
        from paper2saas.tools import SemanticScholarTools
        
        tools = SemanticScholarTools()
        
        assert hasattr(tools, "get_paper_sync")
        assert hasattr(tools, "search_papers_sync")
        assert hasattr(tools, "find_application_papers_sync")
        assert callable(tools.get_paper_sync)
    
    def test_application_keywords(self):
        """SemanticScholarTools should have application keywords defined."""
        from paper2saas.tools import SemanticScholarTools
        
        tools = SemanticScholarTools()
        
        assert "application" in tools.application_keywords
        assert "implementation" in tools.application_keywords
        assert len(tools.application_keywords) > 5


class TestS2AsyncClient:
    """Tests for S2AsyncClient"""
    
    def test_initialization(self, mock_s2_config):
        """S2AsyncClient should initialize with config."""
        from paper2saas.tools.http_client import S2AsyncClient
        
        client = S2AsyncClient(config=mock_s2_config)
        
        assert client.config == mock_s2_config
        assert client._client is None  # Lazy initialization
    
    def test_cache_key_generation(self, mock_s2_config):
        """Cache key should be deterministic."""
        from paper2saas.tools.http_client import S2AsyncClient
        
        client = S2AsyncClient(config=mock_s2_config)
        
        key1 = client._cache_key("paper/123", query="test")
        key2 = client._cache_key("paper/123", query="test")
        key3 = client._cache_key("paper/456", query="test")
        
        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different inputs = different key
