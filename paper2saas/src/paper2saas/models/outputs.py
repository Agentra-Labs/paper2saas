"""Structured output models for agents (anti-hallucination).

Uses Pydantic V2 idioms: `min_length`/`max_length` instead of deprecated
`min_items`/`max_items`, and modern Python 3.12+ type syntax.
"""

from typing import Literal

from pydantic import BaseModel, Field

# --- STRUCTURED OUTPUT MODELS ---


class PaperAnalysisOutput(BaseModel):
    """Enforces structured output to prevent freeform hallucination"""

    paper_title: str = Field(..., description="Exact title from source")
    arxiv_id: str = Field(..., description="The arXiv paper ID")
    authors: list[str] = Field(default_factory=list)
    executive_summary: str = Field(..., description="Executive summary of the paper")
    core_innovations: list[str] = Field(..., min_length=1, max_length=7)
    technical_architecture: str = Field(default="Not explicitly stated in paper")
    limitations: list[str] = Field(default_factory=list)
    applications: list[str] = Field(default_factory=list)
    key_metrics: str = Field(default="None reported")
    data_sources_used: list[str] = Field(..., description="Tools that successfully retrieved data")
    tool_failures: list[str] = Field(default_factory=list, description="Tools that failed")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    unverified_claims: list[str] = Field(default_factory=list)


class MarketSignal(BaseModel):
    signal: str
    source: str
    date_retrieved: str


class PainPoint(BaseModel):
    description: str
    affected_segment: str
    evidence: str
    source: str


class MarketResearchOutput(BaseModel):
    signals: list[MarketSignal] = Field(default_factory=list)
    pain_points: list[PainPoint] = Field(default_factory=list)
    opportunity_areas: list[str] = Field(default_factory=list)
    data_gaps: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"] = "LOW"


class SaaSIdea(BaseModel):
    name: str
    core_concept: str
    target_market: str
    value_proposition: str
    technical_approach: str
    competitive_moat: str
    revenue_model: str
    implementation_complexity: Literal["Low", "Medium", "High"]
    complexity_reason: str
    mvp_features: list[str] = Field(..., min_length=3, max_length=5)
    paper_innovation_link: str = Field(..., description="Which paper innovation enables this")
    market_pain_link: str = Field(..., description="Which pain point this addresses")
    feasibility_score: float = Field(..., ge=0.0, le=10.0)


class IdeaGeneratorOutput(BaseModel):
    ideas: list[SaaSIdea] = Field(..., min_length=5, max_length=10)
    ranking: list[str] = Field(..., description="Ordered list of idea names by score")
    methodology_notes: str = Field(..., description="How ideas were derived from inputs")


class GitHubRepo(BaseModel):
    url: str
    stars: int
    description: str
    language: str
    relevance_score: float = Field(..., ge=0.0, le=10.0)
    source: Literal["paper", "similar_paper", "search"]


class ImplementationComponent(BaseModel):
    component_name: str
    description: str
    github_reference: str | None = None
    complexity: Literal["Low", "Medium", "High"]
    estimated_hours: int
    dependencies: list[str] = Field(default_factory=list)


class ProductEngineerOutput(BaseModel):
    idea_name: str
    github_repos_found: list[GitHubRepo] = Field(default_factory=list)
    recommended_repo: str | None = None
    technical_approach: str
    implementation_components: list[ImplementationComponent] = Field(..., min_length=3)
    architecture_diagram: str
    tech_stack_recommendation: list[str] = Field(..., min_length=3)
    mvp_timeline: str
    code_snippets: list[str] = Field(default_factory=list)
    potential_challenges: list[str] = Field(default_factory=list)
    github_search_queries_used: list[str] = Field(default_factory=list)
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"]


# --- INPUT SCHEMA ---


class Paper2SaaSInput(BaseModel):
    arxiv_id: str = Field(..., description="The arXiv paper ID to analyze")
