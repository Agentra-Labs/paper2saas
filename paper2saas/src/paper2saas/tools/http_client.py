"""
Async HTTP Client with Rate Limiting and Caching

Reusable infrastructure for API integrations with:
- Token bucket rate limiting
- LRU caching with TTL
- Exponential backoff on failures
- Connection pooling
"""

from __future__ import annotations

import asyncio
import hashlib
import time
import logging

import httpx
import backoff
from cachetools import TTLCache

from .s2_config import S2Config


logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls"""

    def __init__(self, rate: float = 100.0, per: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            rate: Number of tokens (requests) allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request token is available."""
        async with self._lock:
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(self.rate, self.tokens + time_passed * (self.rate / self.per))
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) * (self.per / self.rate)
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1


class S2AsyncClient:
    """Async HTTP client with connection pooling and rate limiting"""

    def __init__(self, config: S2Config):
        self.config = config
        self.rate_limiter = RateLimiter(rate=config.requests_per_second)
        self.search_limiter = RateLimiter(rate=config.search_rate_limit)

        # Paper metadata cache
        self._cache: TTLCache = TTLCache(maxsize=config.cache_maxsize, ttl=config.cache_ttl)

        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.config.api_key:
                headers["x-api-key"] = self.config.api_key

            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=httpx.Timeout(
                    connect=self.config.connect_timeout,
                    read=self.config.read_timeout,
                    write=30.0,
                    pool=5.0,
                ),
                limits=httpx.Limits(
                    max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0
                ),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _cache_key(self, endpoint: str, **kwargs) -> str:
        """Generate cache key from endpoint and params."""
        key_str = f"{endpoint}:{sorted(kwargs.items())}"
        return hashlib.md5(key_str.encode()).hexdigest()

    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPStatusError, httpx.ConnectTimeout, httpx.ReadTimeout),
        max_tries=3,
        on_backoff=lambda details: logger.warning(
            "Retry %d: %s", details["tries"], details["exception"]
        ),
    )
    async def _request(
        self,
        method: str,
        url: str,
        use_search_limiter: bool = False,
        use_cache: bool = True,
        **kwargs,
    ) -> dict:
        """Make rate-limited HTTP request with caching."""

        # Check cache first
        if use_cache and method == "GET":
            cache_key = self._cache_key(url, **kwargs.get("params", {}))
            if cache_key in self._cache:
                logger.debug("Cache hit: %s", url)
                return self._cache[cache_key]

        # Apply rate limiting
        limiter = self.search_limiter if use_search_limiter else self.rate_limiter
        await limiter.acquire()

        client = await self._get_client()

        response = await client.request(method, url, **kwargs)
        response.raise_for_status()

        data = response.json()

        # Cache successful GET requests
        if use_cache and method == "GET":
            self._cache[cache_key] = data

        return data

    async def get(self, endpoint: str, use_search_limiter: bool = False, **params) -> dict:
        """GET request to Semantic Scholar API."""
        url = f"{self.config.base_url}/{endpoint}"
        return await self._request("GET", url, use_search_limiter=use_search_limiter, params=params)

    async def post(self, endpoint: str, data: dict, base_url: str | None = None) -> dict:
        """POST request to Semantic Scholar API."""
        url = f"{base_url or self.config.base_url}/{endpoint}"
        return await self._request("POST", url, use_cache=False, json=data)
