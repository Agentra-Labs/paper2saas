"""
Idea-to-SaaS Workflow
Complete pipeline from research paper to validated SaaS concept
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

from ..tools import SemanticScholarTools
from ..analysis import CitationGraphAnalyzer, MarketValidator
from ..models import Paper, MarketValidation

logger = logging.getLogger(__name__)


@dataclass
class SaaSConcept:
    """A generated SaaS product concept"""

    name: str
    description: str
    target_market: str
    value_proposition: str
    source_papers: List[str] = field(default_factory=list)
    validation: Optional[MarketValidation] = None


@dataclass
class IdeaToSaaSResult:
    """Complete result from the Idea-to-SaaS workflow"""

    seed_paper: Dict
    research_lineage: Dict
    research_clusters: List[Dict]
    saas_concepts: List[SaaSConcept]
    validated_concepts: List[SaaSConcept]
    analysis_date: datetime = field(default_factory=datetime.now)


class IdeaToSaaSWorkflow:
    """
    End-to-end workflow: Research Paper → SaaS Product Concepts

    Steps:
    1. Discover related research (similar papers, citations, references)
    2. Build citation graph and detect research clusters
    3. Generate SaaS product concepts from promising clusters
    4. Validate concepts against market reality
    """

    name: str = "Idea to SaaS"
    description: str = "Transform research papers into validated SaaS product concepts"

    def __init__(self):
        self.s2_tools = SemanticScholarTools()
        self.graph_analyzer = CitationGraphAnalyzer()
        self.market_validator = MarketValidator()

    async def run(
        self, seed_paper_id: str, max_concepts: int = 5, validate: bool = True
    ) -> IdeaToSaaSResult:
        """
        Execute the full workflow

        Args:
            seed_paper_id: Semantic Scholar paper ID to start from
            max_concepts: Maximum number of SaaS concepts to generate
            validate: Whether to run market validation

        Returns:
            IdeaToSaaSResult with all discovered concepts
        """
        try:
            # Step 1: Get seed paper and build research lineage
            logger.info(f"Step 1: Building research lineage for {seed_paper_id}")
            lineage = await self.s2_tools.build_research_lineage(seed_paper_id)

            seed_paper = lineage.get("target_paper", {})
            if not seed_paper:
                raise ValueError(f"Could not find paper: {seed_paper_id}")

            # Step 2: Build citation graph
            logger.info("Step 2: Building citation graph")
            self._build_citation_graph(lineage)

            # Step 3: Detect research clusters
            logger.info("Step 3: Detecting research clusters")
            clusters = self.graph_analyzer.detect_communities(min_cluster_size=3)
            cluster_summaries = self.graph_analyzer.get_cluster_summary()

            # Step 4: Generate SaaS concepts from top clusters
            logger.info("Step 4: Generating SaaS concepts")
            concepts = await self._generate_concepts(seed_paper, cluster_summaries[:max_concepts])

            # Step 5: Validate concepts (optional)
            validated = concepts
            if validate:
                logger.info("Step 5: Validating concepts against market")
                validated = await self._validate_concepts(concepts)

            return IdeaToSaaSResult(
                seed_paper=seed_paper,
                research_lineage=lineage,
                research_clusters=cluster_summaries,
                saas_concepts=concepts,
                validated_concepts=validated,
            )

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise

        finally:
            await self.s2_tools.close()

    def _build_citation_graph(self, lineage: Dict) -> None:
        """Build citation graph from lineage data"""
        target = lineage.get("target_paper", {})
        if target:
            paper = Paper(
                id=target.get("id", ""),
                title=target.get("title", ""),
                abstract=target.get("abstract", ""),
                year=target.get("year"),
                authors=target.get("authors", []),
                citation_count=target.get("citation_count", 0),
            )
            self.graph_analyzer.add_paper(paper)

        # Add related papers
        for category in ["similar", "foundations", "derivatives", "applications"]:
            for paper_data in lineage.get(category, []):
                paper = Paper(
                    id=paper_data.get("id", ""),
                    title=paper_data.get("title", ""),
                    abstract=paper_data.get("abstract", ""),
                    year=paper_data.get("year"),
                    authors=paper_data.get("authors", []),
                    citation_count=paper_data.get("citation_count", 0),
                )
                self.graph_analyzer.add_paper(paper)

                # Add citation edges based on category
                if category == "foundations" and target:
                    self.graph_analyzer.add_citation(target["id"], paper.id)
                elif category == "derivatives" and target:
                    self.graph_analyzer.add_citation(paper.id, target["id"])

    async def _generate_concepts(self, seed_paper: Dict, clusters: List[Dict]) -> List[SaaSConcept]:
        """Generate SaaS concepts from research clusters"""
        concepts = []

        for cluster in clusters:
            if cluster.get("application_potential", 0) > 0.3:
                concept = SaaSConcept(
                    name=f"{cluster.get('theme', 'Research')} Platform",
                    description=f"SaaS platform built on {cluster.get('theme', '')} research",
                    target_market="Enterprises and researchers",
                    value_proposition=f"Apply cutting-edge {cluster.get('theme', '')} research",
                    source_papers=[cluster.get("top_paper", seed_paper.get("title", ""))],
                )
                concepts.append(concept)

        return concepts

    async def _validate_concepts(self, concepts: List[SaaSConcept]) -> List[SaaSConcept]:
        """Validate concepts against market"""
        validated = []

        for concept in concepts:
            try:
                validation = await self.market_validator.validate_idea(concept.description)
                concept.validation = validation
                validated.append(concept)
            except Exception as e:
                logger.warning(f"Validation failed for {concept.name}: {e}")
                validated.append(concept)

        return validated
