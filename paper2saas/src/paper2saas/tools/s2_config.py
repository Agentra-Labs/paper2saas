"""
Semantic Scholar API Configuration

Centralized configuration for S2 API access with sensible defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class S2Config:
    """Semantic Scholar API configuration"""

    # API Endpoints
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    recommendations_url: str = "https://api.semanticscholar.org/recommendations/v1"
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("S2_API_KEY"))

    # Rate limiting (free tier: 100 requests per 5 minutes = ~0.33/sec)
    # With API key: 100 requests per second
    requests_per_second: float = 0.33  # Conservative for free tier
    search_rate_limit: float = 0.2  # Search endpoint is more limited

    # Timeouts
    connect_timeout: float = 5.0
    read_timeout: float = 30.0

    # Caching
    cache_ttl: int = 3600  # 1 hour cache TTL
    cache_maxsize: int = 1000  # Max cached items

    # Batch limits
    batch_size: int = 500  # Max papers per batch request

    # Default fields to retrieve
    paper_fields: str = (
        "paperId,title,year,authors,abstract,citationCount,"
        "referenceCount,influentialCitationCount,isOpenAccess,"
        "fieldsOfStudy,s2FieldsOfStudy,publicationTypes,venue,"
        "publicationDate,externalIds"
    )

    citation_fields: str = "paperId,title,year,authors,citationCount,isInfluential,contexts,intents"
