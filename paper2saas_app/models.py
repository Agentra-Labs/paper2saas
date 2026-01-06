from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

# --- STRUCTURED OUTPUT MODELS ---

class PaperAnalysisOutput(BaseModel):
    """Enforces structured output to prevent freeform hallucination"""
    paper_title: str = Field(..., description="Exact title from source")
    arxiv_id: str = Field(..., description="The arXiv paper ID")
    authors: List[str] = Field(default_factory=list)
    executive_summary: str = Field(..., description="Executive summary of the paper")
    core_innovations: List[str] = Field(..., min_items=1, max_items=7)
    technical_architecture: str = Field(default="Not explicitly stated in paper")
    limitations: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    key_metrics: str = Field(default="None reported")
    data_sources_used: List[str] = Field(..., description="Tools that successfully retrieved data")
    tool_failures: List[str] = Field(default_factory=list, description="Tools that failed")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    unverified_claims: List[str] = Field(default_factory=list)


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
    signals: List[MarketSignal] = Field(default_factory=list)
    pain_points: List[PainPoint] = Field(default_factory=list)
    opportunity_areas: List[str] = Field(default_factory=list)
    data_gaps: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
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
    mvp_features: List[str] = Field(..., min_items=3, max_items=5)
    paper_innovation_link: str = Field(..., description="Which paper innovation enables this")
    market_pain_link: str = Field(..., description="Which pain point this addresses")
    feasibility_score: float = Field(..., ge=0.0, le=10.0)


class IdeaGeneratorOutput(BaseModel):
    ideas: List[SaaSIdea] = Field(..., min_items=5, max_items=10)
    ranking: List[str] = Field(..., description="Ordered list of idea names by score")
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
    github_reference: Optional[str] = None
    complexity: Literal["Low", "Medium", "High"]
    estimated_hours: int
    dependencies: List[str] = Field(default_factory=list)


class ProductEngineerOutput(BaseModel):
    idea_name: str
    github_repos_found: List[GitHubRepo] = Field(default_factory=list)
    recommended_repo: Optional[str] = None
    technical_approach: str
    implementation_components: List[ImplementationComponent] = Field(..., min_items=3)
    architecture_diagram: str
    tech_stack_recommendation: List[str] = Field(..., min_items=3)
    mvp_timeline: str
    code_snippets: List[str] = Field(default_factory=list)
    potential_challenges: List[str] = Field(default_factory=list)
    github_search_queries_used: List[str] = Field(default_factory=list)
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"]


# --- INPUT SCHEMA ---

class Paper2SaaSInput(BaseModel):
    arxiv_id: str = Field(..., description="The arXiv paper ID to analyze")


# --- IMPLEMENTATION TEAM OUTPUT MODELS ---

class CodeFile(BaseModel):
    """Represents a single code file in the implementation"""
    file_path: str = Field(..., description="Relative path e.g. src/api/routes.py")
    language: str = Field(..., description="Programming language")
    content: str = Field(..., description="File content")
    description: str = Field(default="", description="Purpose of this file")


class ArchitectureDesign(BaseModel):
    """Output from CodeArchitect agent"""
    idea_name: str
    components: List[str] = Field(..., min_length=2, description="System components")
    architecture_diagram: str = Field(..., description="ASCII diagram of the system")
    tech_stack: Dict[str, str] = Field(..., description="Technology choices with justifications")
    design_rationale: str = Field(..., description="Why this architecture was chosen")
    api_endpoints: List[str] = Field(default_factory=list, description="REST/GraphQL endpoints")
    database_schema: str = Field(default="", description="Database tables/collections")
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"


class ImplementationCode(BaseModel):
    """Output from FullStackEngineer agent"""
    idea_name: str
    files: List[CodeFile] = Field(..., min_length=1)
    setup_instructions: str = Field(..., description="How to set up the project")
    dependencies: List[str] = Field(..., min_length=1, description="npm/pip packages")
    environment_variables: List[str] = Field(default_factory=list)
    run_instructions: str = Field(default="", description="How to run the application")


class DeploymentConfig(BaseModel):
    """Output from DeploymentSpecialist agent"""
    idea_name: str
    dockerfile: str = Field(..., description="Dockerfile content")
    docker_compose: Optional[str] = Field(default=None, description="docker-compose.yml content")
    kubernetes_manifests: Optional[str] = Field(default=None, description="K8s deployment YAML")
    ci_cd_pipeline: str = Field(..., description="GitHub Actions or similar CI/CD workflow")
    environment_setup: str = Field(..., description="Environment variables and secrets setup")
    cloud_provider_notes: str = Field(default="", description="AWS/GCP/Azure specific notes")


class QAStrategy(BaseModel):
    """Output from QAEngineer agent"""
    idea_name: str
    test_cases: List[str] = Field(..., min_length=3, description="Core test cases")
    edge_cases: List[str] = Field(default_factory=list, description="Edge case scenarios")
    integration_test_plan: str = Field(..., description="How to test component integration")
    load_test_approach: str = Field(default="", description="Performance testing strategy")
    security_checklist: List[str] = Field(default_factory=list, description="Security validations")


class ImplementationPackage(BaseModel):
    """Complete implementation package combining all agents' output"""
    idea_name: str
    architecture: ArchitectureDesign
    code: ImplementationCode
    deployment: DeploymentConfig
    qa_strategy: Optional[QAStrategy] = None
    estimated_dev_hours: int = Field(..., description="Estimated hours to build MVP")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
