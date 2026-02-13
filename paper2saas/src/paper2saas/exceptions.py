"""Custom exceptions for Paper2SaaS.

Provides a hierarchy of specific exception types for better error handling
and debugging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from paper2saas.agents.base import AgentContext


class Paper2SaaSError(Exception):
    """Base exception for all Paper2SaaS errors."""

    message: str
    context: AgentContext | None = None

    def __init__(self, message: str, *, context: AgentContext | None = None) -> None:
        self.message = message
        self.context = context
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class PaperError(Paper2SaaSError):
    """Base exception for paper-related errors."""


class PaperNotFoundError(PaperError):
    """Raised when a paper cannot be found or fetched."""

    def __init__(self, paper_id: str) -> None:
        self.paper_id = paper_id
        super().__init__(f"Paper not found: {paper_id}")


class PaperParseError(PaperError):
    """Raised when a paper cannot be parsed."""


class ValidationError(Paper2SaaSError):
    """Base exception for validation-related errors."""


class ModelError(Paper2SaaSError):
    """Base exception for LLM model errors."""


class ModelConfigurationError(ModelError):
    """Raised when model configuration is invalid."""


class ToolError(Paper2SaaSError):
    """Base exception for tool-related errors."""


class ToolNotAvailableError(ToolError):
    """Raised when a required tool is not available."""


class ToolExecutionError(ToolError):
    """Raised when a tool fails during execution."""

    def __init__(self, tool_name: str, message: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {message}")


class TeamError(Paper2SaaSError):
    """Base exception for team/agent coordination errors."""


class DatabaseError(Paper2SaaSError):
    """Base exception for database-related errors."""


def wrap_error(
    exc: BaseException,
    new_message: str,
    *,
    exception_type: type[Paper2SaaSError] = Paper2SaaSError,
) -> Paper2SaaSError:
    """Wrap an exception with a Paper2SaaS exception.

    Args:
        exc: The original exception to wrap.
        new_message: The message for the new exception.
        exception_type: The type of exception to create.

    Returns:
        A new exception of the specified type.
    """
    new_exc = exception_type(new_message)
    if hasattr(exc, "__cause__"):
        new_exc.__cause__ = exc
    return new_exc
