from typing import Any, Callable, Optional, Sequence

from agno.agent import Agent
from agno.tools import Toolkit
from paper2saas.agent_config import AgentConfig
from paper2saas.utils import get_mistral_model, shared_db

def create_agent(
    name: str,
    instructions: str,
    tools: list[Toolkit | Callable] = None,
    model_id: str = AgentConfig.LARGE_MODEL,
    **kwargs: Any,
) -> Agent:
    """
    Factory function to create an Agent with standard configuration.
    
    Applies KISS principle by centralizing common setup:
    - Standard model configuration
    - Shared database connection
    - Markdown output enabled by default
    """
    return Agent(
        name=name,
        model=get_mistral_model(model_id),
        tools=tools or [],
        db=shared_db,
        instructions=instructions,
        markdown=True,
        **kwargs
    )
