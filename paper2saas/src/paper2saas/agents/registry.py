"""
Agent Registry - Centralized agent management with lazy loading

Pattern from ai-agents-architect skill:
- Tool Registry: Dynamic tool discovery and management
- Lazy loading for expensive resources
- Usage tracking for optimization
"""

from functools import lru_cache
from typing import Dict, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from agno.agent import Agent

logger = logging.getLogger(__name__)


# Registry of available agents
_AGENT_REGISTRY: Dict[str, str] = {
    "paper_discovery": "discovery.paper_discovery_agent",
    "application_ideation": "discovery.application_ideation_agent",
    "validation": "validation.validation_agent",
    "ideation": "ideation.ideation_agent",
}

# Cached agent instances
_agent_cache: Dict[str, "Agent"] = {}

# Usage tracking
_usage_counts: Dict[str, int] = {}


def get_agent(name: str) -> "Agent":
    """
    Get an agent by name with lazy loading.

    Args:
        name: Agent identifier (e.g., 'paper_discovery', 'application_ideation')

    Returns:
        Agent instance

    Raises:
        KeyError: If agent name is not registered
    """
    if name not in _AGENT_REGISTRY:
        available = ", ".join(_AGENT_REGISTRY.keys())
        raise KeyError(f"Unknown agent '{name}'. Available: {available}")

    # Lazy load from cache
    if name not in _agent_cache:
        module_path = _AGENT_REGISTRY[name]
        _agent_cache[name] = _load_agent(module_path)
        logger.info(f"Loaded agent: {name}")

    # Track usage
    _usage_counts[name] = _usage_counts.get(name, 0) + 1

    return _agent_cache[name]


def _load_agent(module_path: str) -> "Agent":
    """Dynamically import and return agent from module path."""
    module_name, agent_name = module_path.rsplit(".", 1)

    # Import from paper2saas.agents.<module>
    import importlib

    module = importlib.import_module(f"paper2saas.agents.{module_name}")
    return getattr(module, agent_name)


def list_agents() -> Dict[str, str]:
    """List all available agents with their module paths."""
    return _AGENT_REGISTRY.copy()


def get_usage_stats() -> Dict[str, int]:
    """Get usage counts for each agent (useful for optimization)."""
    return _usage_counts.copy()


def register_agent(name: str, module_path: str) -> None:
    """
    Register a new agent dynamically.

    Args:
        name: Unique identifier for the agent
        module_path: Path to agent in format 'module.agent_variable'
    """
    if name in _AGENT_REGISTRY:
        logger.warning(f"Overwriting existing agent registration: {name}")
    _AGENT_REGISTRY[name] = module_path
    logger.info(f"Registered agent: {name} -> {module_path}")


def clear_cache() -> None:
    """Clear the agent cache (useful for testing or reloading)."""
    _agent_cache.clear()
    logger.info("Agent cache cleared")
