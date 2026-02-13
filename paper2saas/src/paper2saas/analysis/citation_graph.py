"""
Citation Graph Analysis for Research Discovery
Implements graph analysis for discovering research clusters and application pathways
"""

import networkx as nx
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, Counter
import numpy as np
from datetime import datetime
import json
import logging

from ..models import Paper, PaperCluster

logger = logging.getLogger(__name__)


class CitationGraphAnalyzer:
    """Advanced citation graph analysis for research discovery"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.papers: Dict[str, Paper] = {}
        self.clusters: List[PaperCluster] = []

        # Application-indicating keywords
        self.application_keywords = {
            "implementation",
            "system",
            "framework",
            "tool",
            "platform",
            "application",
            "production",
            "deployment",
            "real-world",
            "case study",
            "empirical",
            "practical",
            "industry",
        }

        # Theory-indicating keywords
        self.theory_keywords = {
            "theoretical",
            "analysis",
            "proof",
            "bound",
            "complexity",
            "algorithm",
            "model",
            "approach",
            "method",
            "novel",
        }

    def add_paper(self, paper: Paper) -> None:
        """Add paper to graph"""
        self.papers[paper.id] = paper
        self.graph.add_node(
            paper.id,
            title=paper.title,
            abstract=paper.abstract,
            year=paper.year,
            authors=paper.authors,
            citation_count=paper.citation_count,
        )

    def add_citation(self, citing_paper_id: str, cited_paper_id: str) -> None:
        """Add citation edge (citing -> cited)"""
        self.graph.add_edge(citing_paper_id, cited_paper_id, relation="cites")

    def detect_communities(self, min_cluster_size: int = 3) -> List[PaperCluster]:
        """Detect research communities using Louvain algorithm"""
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()

        # Use Louvain method for community detection
        communities = nx.community.louvain_communities(undirected, seed=42)

        clusters = []
        for idx, community in enumerate(communities):
            if len(community) < min_cluster_size:
                continue

            # Get papers in this community
            community_papers = [
                self.papers[paper_id] for paper_id in community if paper_id in self.papers
            ]

            if not community_papers:
                continue

            # Find central papers (highest PageRank within community)
            subgraph = self.graph.subgraph(community)
            pagerank = nx.pagerank(subgraph)
            central_ids = sorted(pagerank.keys(), key=lambda x: pagerank[x], reverse=True)[:5]
            central_papers = [self.papers[pid] for pid in central_ids if pid in self.papers]

            # Generate theme and metrics
            theme = self._generate_cluster_theme(central_papers)
            app_potential = self._calculate_application_potential(community_papers)
            temporal_trend = self._analyze_temporal_trend(community_papers)

            cluster = PaperCluster(
                id=f"cluster_{idx}",
                papers=community_papers,
                central_papers=central_papers,
                theme=theme,
                application_potential=app_potential,
                temporal_trend=temporal_trend,
            )
            clusters.append(cluster)

        self.clusters = sorted(clusters, key=lambda c: c.application_potential, reverse=True)
        return self.clusters

    def find_application_pathway(self, theory_paper_id: str, max_hops: int = 5) -> List[Dict]:
        """Find citation path from theory to application papers"""
        # Find all application-oriented papers
        app_papers = [
            pid for pid, data in self.graph.nodes(data=True) if self._is_application_paper(data)
        ]

        # Find shortest paths
        pathways = []
        for app_paper_id in app_papers:
            try:
                if nx.has_path(self.graph, theory_paper_id, app_paper_id):
                    path = nx.shortest_path(self.graph, theory_paper_id, app_paper_id)
                    if len(path) <= max_hops + 1:
                        pathways.append(
                            {
                                "target": app_paper_id,
                                "path": path,
                                "length": len(path) - 1,
                                "papers": [self.papers[pid] for pid in path if pid in self.papers],
                            }
                        )
            except nx.NetworkXNoPath:
                continue

        return sorted(pathways, key=lambda x: x["length"])

    def find_cross_domain_bridges(
        self, domain1_keywords: List[str], domain2_keywords: List[str]
    ) -> List[Paper]:
        """Find papers that bridge two different research domains"""
        domain1_papers: Set[str] = set()
        domain2_papers: Set[str] = set()

        # Identify papers in each domain
        for pid, data in self.graph.nodes(data=True):
            title_abstract = (data.get("title", "") + " " + data.get("abstract", "")).lower()

            if any(kw.lower() in title_abstract for kw in domain1_keywords):
                domain1_papers.add(pid)
            if any(kw.lower() in title_abstract for kw in domain2_keywords):
                domain2_papers.add(pid)

        # Find papers that cite both domains
        bridge_papers = []
        for pid in self.graph.nodes():
            if pid in domain1_papers or pid in domain2_papers:
                continue

            cited_papers = set(self.graph.successors(pid))

            cites_domain1 = bool(cited_papers & domain1_papers)
            cites_domain2 = bool(cited_papers & domain2_papers)

            if cites_domain1 and cites_domain2 and pid in self.papers:
                bridge_papers.append(self.papers[pid])

        return sorted(bridge_papers, key=lambda p: p.citation_count, reverse=True)

    def track_research_evolution(
        self, seed_paper_id: str, years_forward: int = 5
    ) -> Dict[int, List[Dict]]:
        """Track how research evolved over time from a seed paper"""
        if seed_paper_id not in self.papers:
            return {}

        seed_paper = self.papers[seed_paper_id]
        seed_year = seed_paper.year or 0

        # Group papers by year
        evolution: Dict[int, List[Dict]] = defaultdict(list)

        # BFS from seed paper
        visited: Set[str] = set()
        queue = [(seed_paper_id, 0)]

        while queue:
            current_id, generation = queue.pop(0)

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id not in self.papers:
                continue

            current_paper = self.papers[current_id]
            paper_year = current_paper.year or 0

            if paper_year <= seed_year + years_forward:
                year_diff = paper_year - seed_year
                evolution[year_diff].append({"paper": current_paper, "generation": generation})

                for citing_id in self.graph.predecessors(current_id):
                    if citing_id not in visited:
                        queue.append((citing_id, generation + 1))

        return dict(evolution)

    def calculate_impact_score(self, paper_id: str) -> Dict[str, float]:
        """Calculate multi-dimensional impact score for a paper"""
        if paper_id not in self.papers:
            return {}

        paper = self.papers[paper_id]

        # Direct citations
        direct_citations = len(list(self.graph.predecessors(paper_id)))

        # PageRank
        pagerank = nx.pagerank(self.graph).get(paper_id, 0)

        # Betweenness centrality
        betweenness = nx.betweenness_centrality(self.graph).get(paper_id, 0)

        # Temporal impact
        recent_citers = [
            self.papers[pid]
            for pid in self.graph.predecessors(paper_id)
            if pid in self.papers and (self.papers[pid].year or 0) >= 2020
        ]
        recent_impact = len(recent_citers) / max(direct_citations, 1)

        return {
            "direct_citations": float(direct_citations),
            "pagerank": pagerank,
            "betweenness": betweenness,
            "recent_impact": recent_impact,
            "composite_score": (
                0.3 * min(direct_citations / 100, 1.0)
                + 0.3 * pagerank * 100
                + 0.2 * betweenness * 10
                + 0.2 * recent_impact
            ),
        }

    def _generate_cluster_theme(self, central_papers: List[Paper]) -> str:
        """Generate theme description from central papers"""
        words = []
        stopwords = {"a", "an", "the", "for", "in", "on", "with", "using", "based"}

        for paper in central_papers[:3]:
            title_words = paper.title.lower().split()
            words.extend([w for w in title_words if w not in stopwords])

        common_words = Counter(words).most_common(3)
        theme_words = [word for word, _ in common_words]

        return " ".join(theme_words).title()

    def _calculate_application_potential(self, papers: List[Paper]) -> float:
        """Score cluster's potential for practical applications"""
        if not papers:
            return 0.0

        score = 0.0

        # Check for application keywords
        app_keyword_count = 0
        for paper in papers:
            text = (paper.title + " " + paper.abstract).lower()
            app_keyword_count += sum(1 for kw in self.application_keywords if kw in text)

        app_keyword_ratio = app_keyword_count / len(papers)
        score += min(app_keyword_ratio * 0.3, 0.3)

        # Recent papers indicate active development
        recent_papers = [p for p in papers if (p.year or 0) >= 2022]
        recency_score = len(recent_papers) / len(papers)
        score += recency_score * 0.3

        # Citation diversity
        avg_citations = float(np.mean([p.citation_count for p in papers]))
        citation_score = min(avg_citations / 100, 1.0)
        score += citation_score * 0.4

        return min(score, 1.0)

    def _analyze_temporal_trend(self, papers: List[Paper]) -> str:
        """Determine if cluster is emerging, mature, or declining"""
        years = [p.year for p in papers if p.year]
        if not years:
            return "unknown"

        recent_years = [y for y in years if y >= 2022]
        old_years = [y for y in years if y < 2020]

        recent_ratio = len(recent_years) / len(papers)

        if recent_ratio > 0.5:
            return "emerging"
        elif len(old_years) > len(recent_years):
            return "declining"
        else:
            return "mature"

    def _is_application_paper(self, paper_data: Dict) -> bool:
        """Check if paper is application-oriented"""
        text = (paper_data.get("title", "") + " " + paper_data.get("abstract", "")).lower()
        return any(kw in text for kw in self.application_keywords)

    def export_graph(self, filepath: str) -> None:
        """Export graph to JSON for visualization"""
        data = {
            "nodes": [
                {
                    "id": pid,
                    "title": self.papers[pid].title,
                    "year": self.papers[pid].year,
                    "citation_count": self.papers[pid].citation_count,
                }
                for pid in self.graph.nodes()
                if pid in self.papers
            ],
            "edges": [
                {"source": u, "target": v, "relation": self.graph[u][v].get("relation", "cites")}
                for u, v in self.graph.edges()
            ],
            "clusters": [
                {
                    "id": cluster.id,
                    "theme": cluster.theme,
                    "paper_count": cluster.paper_count(),
                    "application_potential": cluster.application_potential,
                }
                for cluster in self.clusters
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def get_cluster_summary(self) -> List[Dict]:
        """Get summary of all clusters"""
        return [
            {
                "id": cluster.id,
                "theme": cluster.theme,
                "size": cluster.paper_count(),
                "application_potential": cluster.application_potential,
                "trend": cluster.temporal_trend,
                "top_paper": cluster.central_papers[0].title if cluster.central_papers else "",
                "year_range": cluster.year_range(),
            }
            for cluster in self.clusters
        ]
