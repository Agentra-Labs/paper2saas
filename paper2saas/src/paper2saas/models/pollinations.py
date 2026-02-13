"""Pollinations.ai model provider for Agno agents

Pollinations.ai is a multi-provider gateway that offers access to various
LLM models through an OpenAI-compatible API.

Available models:
- openai, openai-fast, openai-large
- mistral
- gemini, gemini-fast, gemini-large
- deepseek
- grok
- claude, claude-fast, claude-large
- perplexity-fast, perplexity-reasoning
- qwen-coder
- minimax

API Docs: https://github.com/pollinations/pollinations/blob/main/APIDOCS.md
Dashboard: https://enter.pollinations.ai/
"""

from typing import Optional
from agno.models.openai.like import OpenAILike
from ..config import get_settings


class Pollinations(OpenAILike):
    """Pollinations.ai model provider using OpenAI-compatible API.

    Example:
        >>> from paper2saas.models import Pollinations
        >>> from agno.agent import Agent
        >>>
        >>> agent = Agent(model=Pollinations(id="openai"))
        >>> agent.print_response("Hello!")

    Args:
        id: Model identifier. Options: openai, mistral, gemini, deepseek,
            grok, claude, perplexity-fast, etc. See /v1/models for full list.
        api_key: Optional API key. Defaults to POLLINATIONS_API_KEY env var.
        **kwargs: Additional arguments passed to OpenAILike.
    """

    def __init__(self, id: str = "openai", api_key: Optional[str] = None, **kwargs):
        settings = get_settings()
        super().__init__(
            id=id,
            name="Pollinations",
            provider="Pollinations.ai",
            api_key=api_key or settings.pollinations_api_key,
            base_url=settings.pollinations_base_url,
            **kwargs,
        )
