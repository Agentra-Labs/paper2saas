"""Agno toolkits for research discovery

Modules:
- semantic_scholar: Paper discovery and citation analysis
- s2_config: Semantic Scholar API configuration
- http_client: Reusable async HTTP client with rate limiting
"""

from .semantic_scholar import SemanticScholarTools, SemanticScholarToolsSync
from .s2_config import S2Config
from .http_client import S2AsyncClient, RateLimiter

__all__ = [
    # Core toolkit
    "SemanticScholarTools",
    "SemanticScholarToolsSync",
    # Configuration
    "S2Config",
    # HTTP infrastructure
    "S2AsyncClient",
    "RateLimiter",
]
