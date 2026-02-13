"""Paper and research cluster models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
import numpy as np

from paper2saas.models.validation import TemporalTrend


class Paper(BaseModel):
    """Research paper with metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    title: str
    abstract: str = ""
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    citation_count: int = 0
    reference_count: int = 0
    influential_citation_count: int = 0
    venue: str | None = None
    keywords: list[str] = Field(default_factory=list)
    fields_of_study: list[str] = Field(default_factory=list)
    arxiv_id: str | None = None
    doi: str | None = None
    url: str | None = None
    is_open_access: bool = False
    publication_date: str | None = None
    publication_types: list[str] = Field(default_factory=list)

    # Citation context (when retrieved as citation/reference)
    is_influential: bool = False
    contexts: list[str] = Field(default_factory=list)
    intents: list[str] = Field(default_factory=list)

    # Computed metrics
    similarity_score: float = 0.0
    citation_velocity: float = 0.0
    application_score: float = 0.0
    matched_keywords: list[str] = Field(default_factory=list)


class PaperCluster(BaseModel):
    """Cluster of related research papers."""

    id: str
    papers: list[Paper] = Field(default_factory=list)
    central_papers: list[Paper] = Field(default_factory=list)
    theme: str = ""
    application_potential: float = 0.0
    temporal_trend: TemporalTrend = TemporalTrend.UNKNOWN

    def avg_citation_count(self) -> float:
        """Average citation count across cluster."""
        if not self.papers:
            return 0.0
        return float(np.mean([p.citation_count for p in self.papers]))

    def year_range(self) -> tuple[int, int]:
        """Year range of papers in cluster."""
        if not self.papers:
            return (0, 0)
        years = [p.year for p in self.papers if p.year]
        if not years:
            return (0, 0)
        return (min(years), max(years))

    def paper_count(self) -> int:
        """Number of papers in cluster."""
        return len(self.papers)
