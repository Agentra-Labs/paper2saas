"""Market validation models.

Uses Enums instead of string literals for constrained fields,
following Robust Python Ch 8 principles.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Market validation status."""

    CLEAR_OPPORTUNITY = "clear_opportunity"
    CROWDED_MARKET = "crowded_market"
    EMERGING_SPACE = "emerging_space"
    NEEDS_RESEARCH = "needs_research"
    HIGH_RISK = "high_risk"


class MarketPosition(str, Enum):
    """Competitive market position."""

    LEADER = "leader"
    CHALLENGER = "challenger"
    NICHE = "niche"


class RiskLevel(str, Enum):
    """Risk severity level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FundingRound(str, Enum):
    """Startup funding round type."""

    UNKNOWN = "unknown"
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"
    IPO = "ipo"


class FundingTrend(str, Enum):
    """Direction of funding activity."""

    INCREASING = "increasing"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class TemporalTrend(str, Enum):
    """Research area maturity trend."""

    EMERGING = "emerging"
    MATURE = "mature"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class CompetitorAnalysis(BaseModel):
    """Analysis of existing competitor."""

    name: str
    url: str
    description: str = ""
    funding: str | None = None
    founded_year: int | None = None
    market_position: MarketPosition = MarketPosition.CHALLENGER
    similarity_score: float = 0.0


class PatentInfo(BaseModel):
    """Patent information."""

    patent_id: str
    title: str
    assignee: str = "Unknown"
    filing_date: str = "Unknown"
    status: str = "Unknown"
    relevance_score: float = 0.0


class FundingSignal(BaseModel):
    """Funding activity signal."""

    company: str
    amount: str = "Undisclosed"
    date: str = "Unknown"
    investors: list[str] = Field(default_factory=list)
    round_type: FundingRound = FundingRound.UNKNOWN


class MarketValidation(BaseModel):
    """Complete market validation report."""

    idea: str
    status: ValidationStatus
    confidence_score: float = 0.5

    # Market analysis
    competitors: list[CompetitorAnalysis] = Field(default_factory=list)
    market_size_estimate: str | None = None
    growth_rate: str | None = None

    # IP landscape
    relevant_patents: list[PatentInfo] = Field(default_factory=list)
    patent_risk_level: RiskLevel = RiskLevel.LOW

    # Funding signals
    recent_funding: list[FundingSignal] = Field(default_factory=list)
    funding_trend: FundingTrend = FundingTrend.UNKNOWN

    # Key insights
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    # Supporting data
    search_results: list[dict] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.now)

    def competitor_count(self) -> int:
        return len(self.competitors)

    def top_competitors(self, limit: int = 5) -> list[CompetitorAnalysis]:
        return self.competitors[:limit]
