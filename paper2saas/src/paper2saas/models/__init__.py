"""Shared data models and LLM providers for paper2saas platform

Includes:
- Paper models for research data
- Validation models for market analysis
- Structured output models for agents (anti-hallucination)
- LLM provider wrappers
"""

from .paper import Paper, PaperCluster
from .validation import (
    ValidationStatus,
    MarketPosition,
    RiskLevel,
    FundingRound,
    FundingTrend,
    TemporalTrend,
    CompetitorAnalysis,
    PatentInfo,
    FundingSignal,
    MarketValidation,
)
from .pollinations import Pollinations
from .outputs import (
    PaperAnalysisOutput,
    MarketResearchOutput,
    MarketSignal,
    PainPoint,
    SaaSIdea,
    IdeaGeneratorOutput,
    GitHubRepo,
    ImplementationComponent,
    ProductEngineerOutput,
    Paper2SaaSInput,
)

__all__ = [
    # Data models
    "Paper",
    "PaperCluster",
    # Enums (constrained types)
    "ValidationStatus",
    "MarketPosition",
    "RiskLevel",
    "FundingRound",
    "FundingTrend",
    "TemporalTrend",
    # Validation models
    "CompetitorAnalysis",
    "PatentInfo",
    "FundingSignal",
    "MarketValidation",
    # Structured outputs (anti-hallucination)
    "PaperAnalysisOutput",
    "MarketResearchOutput",
    "MarketSignal",
    "PainPoint",
    "SaaSIdea",
    "IdeaGeneratorOutput",
    "GitHubRepo",
    "ImplementationComponent",
    "ProductEngineerOutput",
    "Paper2SaaSInput",
    # LLM providers
    "Pollinations",
]

