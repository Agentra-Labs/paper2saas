"""Optional tools loader

Handles loading of tools that require API keys or optional dependencies.
Returns None if the tool cannot be loaded, allowing graceful degradation.
"""

from __future__ import annotations

import os
import logging

from typing import Any

logger = logging.getLogger(__name__)


def get_optional_tools() -> list[Any]:
    """
    Get list of optional tools that are available based on API keys.

    Returns:
        List of tool instances that were successfully loaded
    """
    tools = []

    # FirecrawlTools - requires FIRECRAWL_API_KEY
    if os.getenv("FIRECRAWL_API_KEY"):
        try:
            from agno.tools.firecrawl import FirecrawlTools

            tools.append(FirecrawlTools(enable_search=True, enable_scrape=True))
            logger.debug("FirecrawlTools loaded")
        except Exception as e:
            logger.warning("Failed to load FirecrawlTools: %s", e)

    # BaiduSearchTools - requires pycountry
    try:
        from agno.tools.baidusearch import BaiduSearchTools

        tools.append(BaiduSearchTools())
        logger.debug("BaiduSearchTools loaded")
    except ImportError:
        pass
    except Exception as e:
        logger.warning("Failed to load BaiduSearchTools: %s", e)

    return tools


def get_firecrawl_tools() -> Any | None:
    """Get FirecrawlTools if API key is available."""
    if not os.getenv("FIRECRAWL_API_KEY"):
        return None
    try:
        from agno.tools.firecrawl import FirecrawlTools

        return FirecrawlTools(enable_search=True, enable_scrape=True)
    except Exception:
        return None


def get_baidu_tools() -> Any | None:
    """Get BaiduSearchTools if available."""
    try:
        from agno.tools.baidusearch import BaiduSearchTools

        return BaiduSearchTools()
    except Exception:
        return None
