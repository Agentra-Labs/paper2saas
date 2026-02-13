"""
Semantic Scholar Tools for Agno

Ultra-fast, async, efficient academic paper discovery using Semantic Scholar API.

This module provides the SemanticScholarTools toolkit which integrates with Agno
agents to enable paper discovery, citation analysis, and research lineage building.

Features:
- Batch operations for bulk lookups
- Native ML-based recommendations
- Citation intent analysis
- Research frontier detection
"""

import asyncio
from datetime import datetime
from typing import Any
import logging

from agno.tools import Toolkit

# Import from extracted modules (SRP compliance)
from .s2_config import S2Config
from .http_client import S2AsyncClient


logger = logging.getLogger(__name__)


# =============================================================================
# SEMANTIC SCHOLAR TOOLS
# =============================================================================


class SemanticScholarTools(Toolkit):
    """
    Agno toolkit for Semantic Scholar API

    Ultra-fast, async alternative to ConnectedPapersTools with:
    - Async HTTP with connection pooling
    - Smart caching (1hr TTL)
    - Batch operations (up to 500 papers/request)
    - Native ML-based recommendations
    - Citation intent analysis
    - Highly influential citations
    """

    def __init__(self, config: S2Config | None = None):
        self.config = config or S2Config()
        self.client = S2AsyncClient(self.config)

        self.application_keywords = [
            "application",
            "implementation",
            "system",
            "framework",
            "tool",
            "platform",
            "deployment",
            "production",
            "case study",
            "empirical",
            "real-world",
            "practical",
            "industry",
            "benchmark",
        ]

        # Use higher rate limits if API key is available
        if self.config.api_key:
            self.config.requests_per_second = 100.0
            self.config.search_rate_limit = 1.0
            logger.info("S2_API_KEY detected - using higher rate limits (100 req/sec)")

        # Register tools with Agno
        # Sync tools for agent.run() / agent.print_response()
        tools = [
            self.get_paper_sync,
            self.search_papers_sync,
            self.find_application_papers_sync,
        ]

        # Async tools for agent.arun() / agent.aprint_response()
        # Format: (async_method, "tool_name")
        async_tools = [
            (self.get_paper, "get_paper_sync"),
            (self.search_papers, "search_papers_sync"),
            (self.find_application_papers, "find_application_papers_sync"),
        ]

        super().__init__(name="semantic_scholar", tools=tools, async_tools=async_tools)

    # =========================================================================
    # SYNC WRAPPERS (required by Agno Toolkit for synchronous execution)
    # =========================================================================

    def _run_async(self, coro):
        """Run an async coroutine in a sync context, works in thread pools too."""
        try:
            # Try to get existing event loop (works in main thread)
            loop = asyncio.get_running_loop()
            # If we're already in an async context, we can't use run_until_complete
            # This shouldn't happen with Agno's sync execution, but just in case
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        except RuntimeError:
            # No running loop - safe to use asyncio.run()
            return asyncio.run(coro)

    def get_paper_sync(self, paper_id: str) -> dict:
        """
        Get detailed information about a single paper.

        Args:
            paper_id: Semantic Scholar ID, ArXiv ID, DOI, ACL ID, etc.
                      Prefix required for non-S2 IDs: 'arXiv:1706.03762', 'DOI:...', etc.

        Returns:
            Paper metadata dictionary with id, title, authors, year, abstract, citation_count
        """
        return self._run_async(self.get_paper(paper_id))

    def search_papers_sync(self, query: str, limit: int = 10) -> list[dict]:
        """
        Search for papers using keywords or natural language.

        Args:
            query: Search query (keywords or natural language description)
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of matching papers with id, title, authors, year, abstract, citation_count
        """
        return self._run_async(self.search_papers(query, limit=limit))

    def find_application_papers_sync(self, paper_id: str, limit: int = 10) -> list[dict]:
        """
        Find papers that represent practical applications or implementations of research.

        Args:
            paper_id: Target paper identifier to find applications of
            limit: Maximum number of application papers to return (default: 10)

        Returns:
            List of application-oriented papers with matched_keywords and application_score
        """
        return self._run_async(self.find_application_papers(paper_id, limit=limit))

    async def close(self) -> None:
        """Clean up resources"""
        await self.client.close()

    # =========================================================================
    # CORE METHODS (matching ConnectedPapers API)
    # =========================================================================

    async def get_paper(self, paper_id: str) -> dict:
        """
        Get detailed information about a single paper.

        Args:
            paper_id: Semantic Scholar ID, ArXiv ID, DOI, ACL ID, etc.
                      Prefix required for non-S2 IDs: 'arXiv:1706.03762', 'DOI:...', etc.

        Returns:
            Paper metadata dictionary
        """
        try:
            result = await self.client.get(f"paper/{paper_id}", fields=self.config.paper_fields)
            return self._normalize_paper(result)
        except Exception as e:
            logger.error("Error fetching paper %s: %s", paper_id, e)
            return {}

    async def get_similar_papers(self, paper_id: str, limit: int = 10) -> list[dict]:
        """
        Find papers similar to the given paper using ML-based recommendations.

        Uses Semantic Scholar's native recommendation engine which considers:
        - Citation relationships
        - Semantic similarity
        - Co-citation patterns

        Args:
            paper_id: Paper identifier
            limit: Maximum number of similar papers to return

        Returns:
            List of similar papers with relevance metadata
        """
        try:
            result = await self.client.post(
                "papers/",
                data={"positivePaperIds": [paper_id], "negativePaperIds": []},
                base_url=self.config.recommendations_url,
            )

            papers = result.get("recommendedPapers", [])[:limit]
            return [self._normalize_paper(p) for p in papers]

        except Exception as e:
            logger.error("Error finding similar papers for %s: %s", paper_id, e)
            return []

    async def get_prior_works(self, paper_id: str, limit: int = 10) -> list[dict]:
        """
        Get foundational papers that the target paper builds upon.
        These are papers referenced by the target paper.

        Args:
            paper_id: Target paper identifier
            limit: Maximum number of prior works to return

        Returns:
            List of referenced papers, sorted by citation count
        """
        try:
            result = await self.client.get(
                f"paper/{paper_id}/references",
                fields=self.config.citation_fields,
                limit=limit * 2,  # Fetch more to allow filtering
            )

            references = result.get("data", [])
            papers = []

            for ref in references:
                cited_paper = ref.get("citedPaper", {})
                if cited_paper and cited_paper.get("paperId"):
                    paper = self._normalize_paper(cited_paper)
                    paper["is_influential"] = ref.get("isInfluential", False)
                    paper["contexts"] = ref.get("contexts", [])
                    paper["intents"] = ref.get("intents", [])
                    papers.append(paper)

            # Sort by citation count (most impactful foundations first)
            papers.sort(key=lambda x: x.get("citation_count", 0), reverse=True)

            logger.info("Found %d prior works for %s", len(papers), paper_id)
            return papers[:limit]

        except Exception as e:
            logger.error("Error finding prior works for %s: %s", paper_id, e)
            return []

    async def get_derivative_works(
        self,
        paper_id: str,
        limit: int = 10,
        recent_only: bool = False,
        influential_only: bool = False,
    ) -> list[dict]:
        """
        Get papers that built upon or cite the target paper.

        Args:
            paper_id: Target paper identifier
            limit: Maximum number of derivative works to return
            recent_only: If True, only return papers from last 2 years
            influential_only: If True, only return highly influential citations

        Returns:
            List of citing papers, sorted by year (newest first)
        """
        try:
            result = await self.client.get(
                f"paper/{paper_id}/citations",
                fields=self.config.citation_fields,
                limit=min(limit * 3, 1000),  # Fetch more for filtering
            )

            citations = result.get("data", [])
            current_year = datetime.now().year
            papers = []

            for cit in citations:
                citing_paper = cit.get("citingPaper", {})
                if not citing_paper or not citing_paper.get("paperId"):
                    continue

                is_influential = cit.get("isInfluential", False)

                # Apply influential filter
                if influential_only and not is_influential:
                    continue

                paper = self._normalize_paper(citing_paper)
                paper["is_influential"] = is_influential
                paper["contexts"] = cit.get("contexts", [])
                paper["intents"] = cit.get("intents", [])

                # Apply recency filter
                if recent_only:
                    paper_year = paper.get("year", 0)
                    if paper_year < current_year - 2:
                        continue

                papers.append(paper)

            # Sort by year (newest first)
            papers.sort(key=lambda x: x.get("year", 0), reverse=True)

            logger.info("Found %d derivative works for %s", len(papers), paper_id)
            return papers[:limit]

        except Exception as e:
            logger.error("Error finding derivative works for %s: %s", paper_id, e)
            return []

    async def find_application_papers(self, paper_id: str, limit: int = 10) -> list[dict]:
        """
        Find papers that represent practical applications or implementations.

        Identifies papers with keywords like: implementation, system, application, etc.
        Combined with citation intent analysis for better accuracy.

        Args:
            paper_id: Target paper identifier
            limit: Maximum number of application papers to return

        Returns:
            List of application-oriented papers
        """
        try:
            # Get all citing papers with intent information
            result = await self.client.get(
                f"paper/{paper_id}/citations", fields=self.config.citation_fields, limit=500
            )

            citations = result.get("data", [])
            applications = []

            for cit in citations:
                citing_paper = cit.get("citingPaper", {})
                if not citing_paper or not citing_paper.get("paperId"):
                    continue

                title = citing_paper.get("title", "").lower()
                intents = cit.get("intents", [])

                # Score based on keywords and intents
                keyword_matches = [kw for kw in self.application_keywords if kw in title]

                # "methodology" and "result" intents indicate practical usage
                has_practical_intent = any(i in intents for i in ["methodology", "result"])

                if keyword_matches or has_practical_intent:
                    paper = self._normalize_paper(citing_paper)
                    paper["matched_keywords"] = keyword_matches
                    paper["intents"] = intents
                    paper["is_influential"] = cit.get("isInfluential", False)

                    # Calculate application score
                    paper["application_score"] = (
                        len(keyword_matches) * 2
                        + (3 if has_practical_intent else 0)
                        + (2 if cit.get("isInfluential") else 0)
                    )
                    applications.append(paper)

            # Sort by application score
            applications.sort(key=lambda x: x.get("application_score", 0), reverse=True)

            logger.info("Found %d application papers for %s", len(applications), paper_id)
            return applications[:limit]

        except Exception as e:
            logger.error("Error finding application papers for %s: %s", paper_id, e)
            return []

    async def build_research_lineage(self, paper_id: str) -> dict:
        """
        Build complete research lineage for a paper:
        - Target paper metadata
        - Foundational papers (references)
        - Derivative works (citations)
        - Similar papers (recommendations)
        - Application papers (practical implementations)
        - Research frontier (recent high-impact)

        Args:
            paper_id: Target paper identifier

        Returns:
            Dictionary with complete lineage
        """
        try:
            # Parallel fetching for speed
            target_task = asyncio.create_task(self.get_paper(paper_id))
            similar_task = asyncio.create_task(self.get_similar_papers(paper_id, limit=10))
            prior_task = asyncio.create_task(self.get_prior_works(paper_id, limit=10))
            derivative_task = asyncio.create_task(self.get_derivative_works(paper_id, limit=10))
            applications_task = asyncio.create_task(
                self.find_application_papers(paper_id, limit=10)
            )
            frontier_task = asyncio.create_task(self.find_research_frontier(paper_id, years_back=2))
            influential_task = asyncio.create_task(
                self.get_highly_influential_citations(paper_id, limit=5)
            )

            results = await asyncio.gather(
                target_task,
                similar_task,
                prior_task,
                derivative_task,
                applications_task,
                frontier_task,
                influential_task,
                return_exceptions=True,
            )

            lineage = {
                "target_paper": results[0] if not isinstance(results[0], Exception) else {},
                "similar": results[1] if not isinstance(results[1], Exception) else [],
                "foundations": results[2] if not isinstance(results[2], Exception) else [],
                "derivatives": results[3] if not isinstance(results[3], Exception) else [],
                "applications": results[4] if not isinstance(results[4], Exception) else [],
                "frontier": results[5] if not isinstance(results[5], Exception) else [],
                "highly_influential": results[6] if not isinstance(results[6], Exception) else [],
                "metadata": {
                    "analysis_date": datetime.now().isoformat(),
                    "api": "semantic_scholar",
                    "paper_id": paper_id,
                },
            }

            logger.info("Built research lineage for %s", paper_id)
            return lineage

        except Exception as e:
            logger.error("Error building research lineage for %s: %s", paper_id, e)
            return {
                "error": str(e),
                "target_paper": {},
                "similar": [],
                "foundations": [],
                "derivatives": [],
                "applications": [],
                "frontier": [],
                "highly_influential": [],
            }

    async def find_research_frontier(
        self, paper_id: str, years_back: int = 2, limit: int = 10
    ) -> list[dict]:
        """
        Find cutting-edge papers at the research frontier.

        Returns recent papers with high citation velocity (citations per year),
        indicating fast-growing research directions.

        Args:
            paper_id: Target paper identifier
            years_back: How many years back to look
            limit: Maximum papers to return

        Returns:
            List of frontier papers with citation velocity metrics
        """
        try:
            current_year = datetime.now().year
            cutoff_year = current_year - years_back

            # Get recent citing papers
            result = await self.client.get(
                f"paper/{paper_id}/citations", fields=self.config.citation_fields, limit=500
            )

            citations = result.get("data", [])
            frontier = []

            for cit in citations:
                citing_paper = cit.get("citingPaper", {})
                if not citing_paper or not citing_paper.get("paperId"):
                    continue

                paper_year = citing_paper.get("year", 0)
                if paper_year < cutoff_year:
                    continue

                citation_count = citing_paper.get("citationCount", 0)
                years_since = max(current_year - paper_year, 0.5)  # Avoid division by zero
                citation_velocity = citation_count / years_since

                paper = self._normalize_paper(citing_paper)
                paper["citation_velocity"] = round(citation_velocity, 2)
                paper["is_influential"] = cit.get("isInfluential", False)

                frontier.append(paper)

            # Sort by citation velocity (hot papers first)
            frontier.sort(key=lambda x: x.get("citation_velocity", 0), reverse=True)

            logger.info("Found %d frontier papers for %s", len(frontier), paper_id)
            return frontier[:limit]

        except Exception as e:
            logger.error("Error finding research frontier for %s: %s", paper_id, e)
            return []

    async def find_cross_domain_papers(
        self, paper_id1: str, paper_id2: str, limit: int = 10
    ) -> list[dict]:
        """
        Find papers that bridge two different research areas.

        These are papers that cite or are cited by both input papers,
        representing novel cross-domain connections.

        Args:
            paper_id1: First paper identifier
            paper_id2: Second paper identifier
            limit: Maximum bridge papers to return

        Returns:
            List of bridge papers connecting the two domains
        """
        try:
            # Get citations for both papers in parallel
            cit1_task = self.client.get(
                f"paper/{paper_id1}/citations", fields="paperId,title,year,citationCount", limit=500
            )
            cit2_task = self.client.get(
                f"paper/{paper_id2}/citations", fields="paperId,title,year,citationCount", limit=500
            )
            ref1_task = self.client.get(
                f"paper/{paper_id1}/references",
                fields="paperId,title,year,citationCount",
                limit=500,
            )
            ref2_task = self.client.get(
                f"paper/{paper_id2}/references",
                fields="paperId,title,year,citationCount",
                limit=500,
            )

            cit1, cit2, ref1, ref2 = await asyncio.gather(
                cit1_task, cit2_task, ref1_task, ref2_task
            )

            # Extract paper IDs from all connections
            def extract_ids(data: dict, key: str) -> set[str]:
                papers = data.get("data", [])
                return {
                    p.get(key, {}).get("paperId") for p in papers if p.get(key, {}).get("paperId")
                }

            cit1_ids = extract_ids(cit1, "citingPaper")
            cit2_ids = extract_ids(cit2, "citingPaper")
            ref1_ids = extract_ids(ref1, "citedPaper")
            ref2_ids = extract_ids(ref2, "citedPaper")

            # Find intersection (papers connected to both)
            all_ids1 = cit1_ids | ref1_ids
            all_ids2 = cit2_ids | ref2_ids
            bridge_ids = all_ids1 & all_ids2

            if not bridge_ids:
                logger.info("No bridge papers found between %s and %s", paper_id1, paper_id2)
                return []

            # Fetch full details for bridge papers
            bridge_papers = await self.batch_get_papers(list(bridge_ids)[:limit])

            # Sort by citation count
            bridge_papers.sort(key=lambda x: x.get("citation_count", 0), reverse=True)

            logger.info("Found %d bridge papers", len(bridge_papers))
            return bridge_papers

        except Exception as e:
            logger.error("Error finding cross-domain papers: %s", e)
            return []

    # =========================================================================
    # ENHANCED METHODS (new capabilities)
    # =========================================================================

    async def get_recommendations(
        self,
        positive_paper_ids: list[str],
        negative_paper_ids: list[str] | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Get ML-based paper recommendations from multiple examples.

        Uses positive examples to find similar papers and negative examples
        to filter out unwanted directions.

        Args:
            positive_paper_ids: Papers representing desired research direction
            negative_paper_ids: Papers to avoid (optional)
            limit: Maximum recommendations to return

        Returns:
            List of recommended papers
        """
        try:
            result = await self.client.post(
                "papers/",
                data={
                    "positivePaperIds": positive_paper_ids,
                    "negativePaperIds": negative_paper_ids or [],
                },
                base_url=self.config.recommendations_url,
            )

            papers = result.get("recommendedPapers", [])[:limit]
            return [self._normalize_paper(p) for p in papers]

        except Exception as e:
            logger.error("Error getting recommendations: %s", e)
            return []

    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        year_range: tuple | None = None,
        fields_of_study: list[str] | None = None,
        open_access_only: bool = False,
    ) -> list[dict]:
        """
        Search for papers using keywords/natural language.

        Args:
            query: Search query (keywords or natural language)
            limit: Maximum results to return
            year_range: Optional (start_year, end_year) tuple
            fields_of_study: Filter by fields (e.g., ["Computer Science", "Medicine"])
            open_access_only: Only return open access papers

        Returns:
            List of matching papers sorted by relevance
        """
        try:
            params = {"query": query, "limit": min(limit, 100), "fields": self.config.paper_fields}

            if year_range:
                params["year"] = f"{year_range[0]}-{year_range[1]}"

            if fields_of_study:
                params["fieldsOfStudy"] = ",".join(fields_of_study)

            if open_access_only:
                params["openAccessPdf"] = ""

            result = await self.client.get("paper/search", use_search_limiter=True, **params)

            papers = result.get("data", [])
            return [self._normalize_paper(p) for p in papers]

        except Exception as e:
            logger.error("Error searching papers for '%s': %s", query, e)
            return []

    async def batch_get_papers(self, paper_ids: list[str]) -> list[dict]:
        """
        Get details for multiple papers in a single batch request.

        Much more efficient than individual requests when fetching
        many papers (up to 500 per request).

        Args:
            paper_ids: List of paper identifiers

        Returns:
            List of paper details
        """
        try:
            all_papers = []

            # Process in batches of 500
            for i in range(0, len(paper_ids), self.config.batch_size):
                batch = paper_ids[i : i + self.config.batch_size]

                result = await self.client.post(
                    "paper/batch",
                    data={"ids": batch},
                )

                papers = result if isinstance(result, list) else []
                all_papers.extend([self._normalize_paper(p) for p in papers if p])

            return all_papers

        except Exception as e:
            logger.error("Error in batch paper lookup: %s", e)
            return []

    async def get_author_papers(self, author_id: str, limit: int = 20) -> list[dict]:
        """
        Get papers by a specific author.

        Args:
            author_id: Semantic Scholar author ID
            limit: Maximum papers to return

        Returns:
            List of author's papers sorted by citation count
        """
        try:
            result = await self.client.get(
                f"author/{author_id}/papers", fields=self.config.paper_fields, limit=limit
            )

            papers = result.get("data", [])
            normalized = [self._normalize_paper(p) for p in papers]

            # Sort by citation count
            normalized.sort(key=lambda x: x.get("citation_count", 0), reverse=True)

            return normalized

        except Exception as e:
            logger.error("Error getting author papers for %s: %s", author_id, e)
            return []

    async def get_highly_influential_citations(self, paper_id: str, limit: int = 10) -> list[dict]:
        """
        Get only the highly influential citations for a paper.

        Semantic Scholar marks citations as "influential" when they
        have significant impact on the citing paper's methodology or results.

        Args:
            paper_id: Target paper identifier
            limit: Maximum influential citations to return

        Returns:
            List of highly influential citing papers
        """
        return await self.get_derivative_works(paper_id, limit=limit, influential_only=True)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _normalize_paper(self, paper: dict) -> dict:
        """Normalize paper data to consistent format"""
        if not paper:
            return {}

        # Handle authors list
        authors = paper.get("authors", [])
        if authors and isinstance(authors[0], dict):
            author_names = [a.get("name", "") for a in authors]
        else:
            author_names = authors

        # Extract external IDs
        external_ids = paper.get("externalIds", {}) or {}

        return {
            "id": paper.get("paperId", ""),
            "title": paper.get("title", ""),
            "year": paper.get("year"),
            "authors": author_names,
            "abstract": paper.get("abstract", ""),
            "citation_count": paper.get("citationCount", 0),
            "reference_count": paper.get("referenceCount", 0),
            "influential_citation_count": paper.get("influentialCitationCount", 0),
            "is_open_access": paper.get("isOpenAccess", False),
            "venue": paper.get("venue", ""),
            "fields_of_study": paper.get("fieldsOfStudy", []),
            "publication_date": paper.get("publicationDate"),
            "publication_types": paper.get("publicationTypes", []),
            "arxiv_id": external_ids.get("ArXiv"),
            "doi": external_ids.get("DOI"),
            "url": f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
        }


# =============================================================================
# SYNC WRAPPER (for non-async contexts)
# =============================================================================


class SemanticScholarToolsSync:
    """Synchronous wrapper for SemanticScholarTools"""

    def __init__(self, config: S2Config | None = None):
        self._async_tools = SemanticScholarTools(config)

    def _run(self, coro):
        """Run async coroutine synchronously"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def get_paper(self, paper_id: str) -> dict:
        return self._run(self._async_tools.get_paper(paper_id))

    def get_similar_papers(self, paper_id: str, limit: int = 10) -> list[dict]:
        return self._run(self._async_tools.get_similar_papers(paper_id, limit))

    def get_prior_works(self, paper_id: str, limit: int = 10) -> list[dict]:
        return self._run(self._async_tools.get_prior_works(paper_id, limit))

    def get_derivative_works(
        self, paper_id: str, limit: int = 10, recent_only: bool = False
    ) -> list[dict]:
        return self._run(self._async_tools.get_derivative_works(paper_id, limit, recent_only))

    def find_application_papers(self, paper_id: str, limit: int = 10) -> list[dict]:
        return self._run(self._async_tools.find_application_papers(paper_id, limit))

    def build_research_lineage(self, paper_id: str) -> dict:
        return self._run(self._async_tools.build_research_lineage(paper_id))

    def find_research_frontier(self, paper_id: str, years_back: int = 2) -> list[dict]:
        return self._run(self._async_tools.find_research_frontier(paper_id, years_back))

    def find_cross_domain_papers(self, paper_id1: str, paper_id2: str) -> list[dict]:
        return self._run(self._async_tools.find_cross_domain_papers(paper_id1, paper_id2))

    def search_papers(self, query: str, limit: int = 10) -> list[dict]:
        return self._run(self._async_tools.search_papers(query, limit))

    def batch_get_papers(self, paper_ids: list[str]) -> list[dict]:
        return self._run(self._async_tools.batch_get_papers(paper_ids))


# =============================================================================
# EXAMPLE USAGE
# =============================================================================


async def main() -> None:
    """Example usage demonstrating all capabilities."""
    tools = SemanticScholarTools()

    # Example: Analyze the Transformer paper (Attention Is All You Need)
    paper_id = "arXiv:1706.03762"

    logger.info("Getting paper details...")
    paper = await tools.get_paper(paper_id)
    if paper:
        logger.info("  Title: %s", paper["title"])
        logger.info("  Citations: %s", f"{paper['citation_count']:,}")
        logger.info("  Influential Citations: %s", f"{paper['influential_citation_count']:,}")

    logger.info("Getting similar papers (recommendations)...")
    similar = await tools.get_similar_papers(paper_id, limit=5)
    for p in similar:
        logger.info("  - %s (%s)", p["title"][:60], p["year"])

    logger.info("Getting foundational papers (references)...")
    foundations = await tools.get_prior_works(paper_id, limit=5)
    for p in foundations:
        logger.info("  - %s (%s cites)", p["title"][:60], f"{p['citation_count']:,}")

    logger.info("Getting derivative works (citations)...")
    derivatives = await tools.get_derivative_works(paper_id, limit=5, recent_only=True)
    for p in derivatives:
        marker = "⭐ " if p.get("is_influential") else ""
        logger.info("  %s%s (%s)", marker, p["title"][:55], p["year"])

    logger.info("Finding application papers...")
    apps = await tools.find_application_papers(paper_id, limit=5)
    for p in apps:
        keywords = ", ".join(p.get("matched_keywords", []))
        logger.info("  - %s [%s]", p["title"][:50], keywords)

    logger.info("Finding research frontier (high velocity papers)...")
    frontier = await tools.find_research_frontier(paper_id, years_back=2, limit=5)
    for p in frontier:
        logger.info("  - %s (%.1f cites/year)", p["title"][:50], p["citation_velocity"])

    logger.info("Getting highly influential citations...")
    influential = await tools.get_highly_influential_citations(paper_id, limit=5)
    for p in influential:
        logger.info("  - %s (%s)", p["title"][:60], p["year"])

    logger.info("Searching for related papers...")
    search_results = await tools.search_papers(
        "transformer attention mechanism neural network", limit=5, year_range=(2022, 2024)
    )
    for p in search_results:
        logger.info("  - %s (%s)", p["title"][:60], p["year"])

    logger.info("Building complete research lineage...")
    lineage = await tools.build_research_lineage(paper_id)
    logger.info("  Foundations: %d papers", len(lineage["foundations"]))
    logger.info("  Similar: %d papers", len(lineage["similar"]))
    logger.info("  Derivatives: %d papers", len(lineage["derivatives"]))
    logger.info("  Applications: %d papers", len(lineage["applications"]))
    logger.info("  Frontier: %d papers", len(lineage["frontier"]))
    logger.info("  Highly Influential: %d papers", len(lineage["highly_influential"]))

    await tools.close()
    logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
