"""
SaaS-to-Improvement Workflow
Find new research that could improve an existing SaaS product
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..tools import SemanticScholarTools
from ..models import Paper

logger = logging.getLogger(__name__)


@dataclass
class ResearchRecommendation:
    """A research-based improvement recommendation"""

    paper: Dict
    improvement_area: str
    potential_impact: str
    implementation_complexity: str
    relevance_score: float


@dataclass
class SaaSImprovementResult:
    """Result from the SaaS improvement workflow"""

    product_description: str
    seed_papers: List[Dict]
    frontier_research: List[Dict]
    recommendations: List[ResearchRecommendation]
    analysis_date: datetime = field(default_factory=datetime.now)


class SaaSToImprovementWorkflow:
    """
    Workflow to find research improvements for existing SaaS products

    Steps:
    1. Identify foundational research for the SaaS product
    2. Find cutting-edge research at the frontier
    3. Identify application-ready papers
    4. Generate improvement recommendations
    """

    name: str = "SaaS to Improvement"
    description: str = "Find research-based improvements for existing SaaS products"

    def __init__(self):
        self.s2_tools = SemanticScholarTools()

    async def run(
        self,
        product_description: str,
        seed_paper_ids: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        max_recommendations: int = 10,
    ) -> SaaSImprovementResult:
        """
        Execute the SaaS improvement workflow

        Args:
            product_description: Description of the SaaS product
            seed_paper_ids: Optional list of known foundational papers
            search_query: Optional search query for finding related papers
            max_recommendations: Maximum recommendations to generate

        Returns:
            SaaSImprovementResult with improvement recommendations
        """
        try:
            # Step 1: Find seed papers if not provided
            logger.info("Step 1: Finding foundational research")
            if seed_paper_ids:
                seed_papers = await self.s2_tools.batch_get_papers(seed_paper_ids)
            elif search_query:
                seed_papers = await self.s2_tools.search_papers(search_query, limit=5)
            else:
                seed_papers = await self.s2_tools.search_papers(product_description, limit=5)

            if not seed_papers:
                raise ValueError("Could not find relevant seed papers")

            # Step 2: Find frontier research for each seed paper
            logger.info("Step 2: Finding frontier research")
            frontier_research = []
            for paper in seed_papers[:3]:
                paper_id = paper.get("id")
                if paper_id:
                    frontier = await self.s2_tools.find_research_frontier(
                        paper_id, years_back=2, limit=5
                    )
                    frontier_research.extend(frontier)

            # Deduplicate
            seen_ids = set()
            unique_frontier = []
            for paper in frontier_research:
                paper_id = paper.get("id")
                if paper_id and paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    unique_frontier.append(paper)

            # Step 3: Find application-ready papers
            logger.info("Step 3: Finding application-ready papers")
            application_papers = []
            for paper in seed_papers[:2]:
                paper_id = paper.get("id")
                if paper_id:
                    apps = await self.s2_tools.find_application_papers(paper_id, limit=5)
                    application_papers.extend(apps)

            # Step 4: Generate recommendations
            logger.info("Step 4: Generating recommendations")
            recommendations = self._generate_recommendations(
                unique_frontier, application_papers, max_recommendations
            )

            return SaaSImprovementResult(
                product_description=product_description,
                seed_papers=seed_papers,
                frontier_research=unique_frontier,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise

        finally:
            await self.s2_tools.close()

    def _generate_recommendations(
        self, frontier_papers: List[Dict], application_papers: List[Dict], max_count: int
    ) -> List[ResearchRecommendation]:
        """Generate improvement recommendations from research"""
        recommendations = []

        # High-velocity frontier papers
        for paper in frontier_papers[: max_count // 2]:
            velocity = paper.get("citation_velocity", 0)
            recommendations.append(
                ResearchRecommendation(
                    paper=paper,
                    improvement_area="Performance / Accuracy",
                    potential_impact="high" if velocity > 10 else "medium",
                    implementation_complexity="medium",
                    relevance_score=min(velocity / 20, 1.0),
                )
            )

        # Application papers
        for paper in application_papers[: max_count // 2]:
            score = paper.get("application_score", 0)
            recommendations.append(
                ResearchRecommendation(
                    paper=paper,
                    improvement_area="New Feature / Capability",
                    potential_impact="high" if score > 5 else "medium",
                    implementation_complexity="low",
                    relevance_score=min(score / 10, 1.0),
                )
            )

        # Sort by relevance
        recommendations.sort(key=lambda r: r.relevance_score, reverse=True)

        return recommendations[:max_count]
