"""
Paper2SaaS - Transform academic arXiv papers into SaaS business opportunities

A multi-agent AI system that analyzes research papers and generates
validated SaaS business opportunities.

Features:
- arXiv paper analysis with fallback protocols
- Market research and validation
- SaaS idea generation
- Technical implementation planning
- Comprehensive opportunity reports

Example:
    >>> from paper2saas.agents import paper_analyzer
    >>> result = paper_analyzer.run("2512.24991v1")
"""

__version__ = "0.1.0"

# Configuration
from .config import get_settings, Settings

# Models
from .models import (
    Paper,
    PaperCluster,
    ValidationStatus,
    CompetitorAnalysis,
    PatentInfo,
    FundingSignal,
    MarketValidation,
)

# Tools
from .tools import SemanticScholarTools, SemanticScholarToolsSync

# Analysis
from .analysis import CitationGraphAnalyzer, MarketValidator

# Workflows
from .workflows import IdeaToSaaSWorkflow, SaaSToImprovementWorkflow

__all__ = [
    # Version
    "__version__",
    # Config
    "get_settings",
    "Settings",
    # Models
    "Paper",
    "PaperCluster",
    "ValidationStatus",
    "CompetitorAnalysis",
    "PatentInfo",
    "FundingSignal",
    "MarketValidation",
    # Tools
    "SemanticScholarTools",
    "SemanticScholarToolsSync",
    # Analysis
    "CitationGraphAnalyzer",
    "MarketValidator",
    # Workflows
    "IdeaToSaaSWorkflow",
    "SaaSToImprovementWorkflow",
]
