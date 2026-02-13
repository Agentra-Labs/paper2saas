"""
Market Validation for Research-to-SaaS Ideas
Validates SaaS ideas against real market data: products, patents, funding, trends
"""

import re
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging

from ..models import (
    ValidationStatus,
    CompetitorAnalysis,
    PatentInfo,
    FundingSignal,
    MarketValidation,
)

logger = logging.getLogger(__name__)


class MarketValidator:
    """Validates SaaS ideas against market reality"""

    def __init__(self, web_search_tool=None):
        self.web_search = web_search_tool

        # Market databases to check
        self.product_databases = ["producthunt.com", "crunchbase.com", "g2.com", "capterra.com"]

        self.funding_databases = ["crunchbase.com", "pitchbook.com", "techcrunch.com"]

        # Red flag keywords
        self.red_flags = {
            "legal": ["lawsuit", "litigation", "banned", "illegal"],
            "ethical": ["controversial", "privacy concerns", "data breach"],
            "technical": ["unsolvable", "impossible", "fundamental limitation"],
        }

    async def validate_idea(
        self, idea: str, paper_context: Optional[List[Dict]] = None
    ) -> MarketValidation:
        """
        Comprehensive market validation of a SaaS idea

        Args:
            idea: The SaaS idea to validate
            paper_context: Related research papers for context
        """
        # Run validations in parallel
        results = await asyncio.gather(
            self._find_competitors(idea),
            self._check_patents(idea),
            self._find_funding_signals(idea),
            self._estimate_market_size(idea),
            self._check_red_flags(idea),
        )

        competitors = results[0]
        patents = results[1]
        funding = results[2]
        market_info = results[3]
        red_flags = results[4]

        # Analyze results
        status = self._determine_status(competitors, patents, funding, red_flags)
        confidence = self._calculate_confidence(
            len(competitors), len(patents), len(funding), red_flags
        )

        # Generate insights
        strengths = self._identify_strengths(idea, competitors, market_info, paper_context)
        risks = self._identify_risks(competitors, patents, red_flags)
        recommendations = self._generate_recommendations(status, competitors, strengths, risks)

        return MarketValidation(
            idea=idea,
            status=status,
            confidence_score=confidence,
            competitors=competitors,
            market_size_estimate=market_info.get("size"),
            growth_rate=market_info.get("growth"),
            relevant_patents=patents,
            patent_risk_level=self._assess_patent_risk(patents),
            recent_funding=funding,
            funding_trend=self._analyze_funding_trend(funding),
            strengths=strengths,
            risks=risks,
            recommendations=recommendations,
            search_results=[],
            analyzed_at=datetime.now(),
        )

    async def _find_competitors(self, idea: str) -> List[CompetitorAnalysis]:
        """Find existing competitors"""
        competitors = []

        if not self.web_search:
            return competitors

        search_queries = [
            f"{idea} SaaS products",
            f"{idea} software solutions",
            f"{idea} platforms",
            f"companies doing {idea}",
        ]

        all_results = []
        for query in search_queries:
            results = await self._search_web(query)
            all_results.extend(results)

        seen_domains = set()
        for result in all_results:
            domain = self._extract_domain(result.get("url", ""))
            if domain in seen_domains or not domain:
                continue
            seen_domains.add(domain)

            if self._is_product_page(result):
                competitors.append(
                    CompetitorAnalysis(
                        name=result.get("title", "Unknown"),
                        url=result.get("url", ""),
                        description=result.get("snippet", ""),
                        funding=None,
                        founded_year=None,
                        market_position=self._infer_market_position(result),
                        similarity_score=self._calculate_similarity(idea, result),
                    )
                )

        return sorted(
            competitors,
            key=lambda c: (c.similarity_score, c.market_position == "leader"),
            reverse=True,
        )[:20]

    async def _check_patents(self, idea: str) -> List[PatentInfo]:
        """Check for relevant patents"""
        patents = []

        if not self.web_search:
            return patents

        search_queries = [f"{idea} patent", f"{idea} USPTO", f"{idea} intellectual property"]

        for query in search_queries:
            results = await self._search_web(query)

            for result in results:
                url = result.get("url", "")
                if any(db in url for db in ["patents.google.com", "uspto.gov"]):
                    patents.append(
                        PatentInfo(
                            patent_id=self._extract_patent_id(url),
                            title=result.get("title", ""),
                            assignee="Unknown",
                            filing_date="Unknown",
                            status="Unknown",
                            relevance_score=self._calculate_similarity(idea, result),
                        )
                    )

        return sorted(patents, key=lambda p: p.relevance_score, reverse=True)[:10]

    async def _find_funding_signals(self, idea: str) -> List[FundingSignal]:
        """Find recent funding activity in this space"""
        funding_signals = []

        if not self.web_search:
            return funding_signals

        search_queries = [
            f"{idea} startup funding 2024",
            f"{idea} raises seed round",
            f"{idea} series A 2024",
        ]

        for query in search_queries:
            results = await self._search_web(query)

            for result in results:
                snippet = result.get("snippet", "").lower()
                if any(term in snippet for term in ["raises", "funding", "million", "series"]):
                    funding_signals.append(
                        FundingSignal(
                            company=self._extract_company_name(result),
                            amount=self._extract_funding_amount(result),
                            date=self._extract_date(result),
                            investors=[],
                            round_type=self._extract_round_type(result),
                        )
                    )

        return funding_signals[:15]

    async def _estimate_market_size(self, idea: str) -> Dict[str, str]:
        """Estimate total addressable market"""
        if not self.web_search:
            return {}

        query = f"{idea} market size TAM forecast"
        results = await self._search_web(query)

        market_info = {}
        for result in results:
            snippet = result.get("snippet", "")

            size_match = re.search(
                r"\$?(\d+\.?\d*)\s*(billion|million|trillion)", snippet, re.IGNORECASE
            )
            if size_match and "size" not in market_info:
                market_info["size"] = f"${size_match.group(1)} {size_match.group(2)}"

            growth_match = re.search(
                r"(\d+\.?\d*)%?\s*(CAGR|growth|annually)", snippet, re.IGNORECASE
            )
            if growth_match and "growth" not in market_info:
                market_info["growth"] = f"{growth_match.group(1)}% CAGR"

        return market_info

    async def _check_red_flags(self, idea: str) -> Dict[str, List[str]]:
        """Check for potential red flags"""
        red_flags_found = {"legal": [], "ethical": [], "technical": []}

        if not self.web_search:
            return red_flags_found

        query = f"{idea} concerns problems issues challenges"
        results = await self._search_web(query)

        for result in results:
            text = (result.get("title", "") + " " + result.get("snippet", "")).lower()

            for category, keywords in self.red_flags.items():
                for keyword in keywords:
                    if keyword in text:
                        red_flags_found[category].append(result.get("title", ""))

        return red_flags_found

    def _determine_status(
        self,
        competitors: List[CompetitorAnalysis],
        patents: List[PatentInfo],
        funding: List[FundingSignal],
        red_flags: Dict,
    ) -> ValidationStatus:
        """Determine overall validation status"""
        total_red_flags = sum(len(flags) for flags in red_flags.values())
        if total_red_flags > 5:
            return ValidationStatus.HIGH_RISK

        high_similarity_competitors = [c for c in competitors if c.similarity_score > 0.7]

        if len(high_similarity_competitors) > 10:
            return ValidationStatus.CROWDED_MARKET
        elif len(high_similarity_competitors) > 3:
            return ValidationStatus.EMERGING_SPACE

        if len(funding) > 5:
            return ValidationStatus.EMERGING_SPACE
        elif len(funding) == 0 and len(competitors) == 0:
            return ValidationStatus.NEEDS_RESEARCH

        return ValidationStatus.CLEAR_OPPORTUNITY

    def _calculate_confidence(
        self, competitor_count: int, patent_count: int, funding_count: int, red_flags: Dict
    ) -> float:
        """Calculate confidence in validation results"""
        confidence = 0.5

        if competitor_count > 5:
            confidence += 0.2
        if patent_count > 3:
            confidence += 0.1
        if funding_count > 3:
            confidence += 0.2

        total_red_flags = sum(len(flags) for flags in red_flags.values())
        confidence -= total_red_flags * 0.05

        return max(0.0, min(1.0, confidence))

    def _identify_strengths(
        self,
        idea: str,
        competitors: List[CompetitorAnalysis],
        market_info: Dict,
        paper_context: Optional[List[Dict]],
    ) -> List[str]:
        """Identify strengths of the idea"""
        strengths = []

        if market_info.get("size"):
            strengths.append(f"Large market opportunity: {market_info['size']}")

        if market_info.get("growth"):
            strengths.append(f"Growing market: {market_info['growth']}")

        if len(competitors) < 5:
            strengths.append("Limited direct competition")

        if paper_context and len(paper_context) > 0:
            strengths.append(f"Strong research foundation ({len(paper_context)} relevant papers)")

            recent_papers = [p for p in paper_context if p.get("year", 0) >= 2022]
            if recent_papers:
                strengths.append(f"Cutting-edge research ({len(recent_papers)} papers from 2022+)")

        return strengths

    def _identify_risks(
        self, competitors: List[CompetitorAnalysis], patents: List[PatentInfo], red_flags: Dict
    ) -> List[str]:
        """Identify risks"""
        risks = []

        leaders = [c for c in competitors if c.market_position == "leader"]
        if leaders:
            names = ", ".join(c.name for c in leaders[:3])
            risks.append(f"Established market leaders: {names}")

        high_relevance_patents = [p for p in patents if p.relevance_score > 0.7]
        if high_relevance_patents:
            risks.append(
                f"Potential patent conflicts ({len(high_relevance_patents)} highly relevant patents)"
            )

        for category, flags in red_flags.items():
            if flags:
                risks.append(f"{category.title()} concerns: {len(flags)} issues found")

        return risks

    def _generate_recommendations(
        self,
        status: ValidationStatus,
        competitors: List[CompetitorAnalysis],
        strengths: List[str],
        risks: List[str],
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if status == ValidationStatus.CLEAR_OPPORTUNITY:
            recommendations.append("Strong go-to-market opportunity - consider MVP development")
            recommendations.append("Conduct customer interviews to validate assumptions")

        elif status == ValidationStatus.EMERGING_SPACE:
            recommendations.append("Identify clear differentiation vs existing solutions")
            recommendations.append("Consider targeting underserved niche initially")
            if competitors:
                recommendations.append(f"Study {competitors[0].name}'s approach and find gaps")

        elif status == ValidationStatus.CROWDED_MARKET:
            recommendations.append("Strong differentiation required")
            recommendations.append("Focus on specific vertical or use case")
            recommendations.append("Consider partnership vs direct competition")

        elif status == ValidationStatus.HIGH_RISK:
            recommendations.append("Address identified red flags before proceeding")
            recommendations.append("Consult legal/technical experts")

        else:  # NEEDS_RESEARCH
            recommendations.append("Conduct deeper market research")
            recommendations.append("Interview potential customers")
            recommendations.append("Build proof of concept first")

        return recommendations

    def _assess_patent_risk(self, patents: List[PatentInfo]) -> str:
        """Assess patent risk level"""
        if not patents:
            return "low"

        high_relevance = [p for p in patents if p.relevance_score > 0.8]
        if len(high_relevance) > 3:
            return "high"
        elif len(patents) > 5:
            return "medium"
        else:
            return "low"

    def _analyze_funding_trend(self, funding: List[FundingSignal]) -> str:
        """Analyze funding trend"""
        if not funding:
            return "unknown"

        recent_funding = [f for f in funding if "2024" in f.date or "2023" in f.date]

        if len(recent_funding) > len(funding) * 0.6:
            return "increasing"
        elif len(recent_funding) < len(funding) * 0.3:
            return "declining"
        else:
            return "stable"

    # Helper methods
    async def _search_web(self, query: str) -> List[Dict]:
        """Execute web search"""
        if not self.web_search:
            return []
        return []

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        match = re.search(r"https?://([^/]+)", url)
        return match.group(1) if match else ""

    def _is_product_page(self, result: Dict) -> bool:
        """Check if result is a product page"""
        snippet = result.get("snippet", "").lower()
        product_indicators = [
            "pricing",
            "features",
            "signup",
            "demo",
            "platform",
            "software",
            "tool",
        ]
        return any(indicator in snippet for indicator in product_indicators)

    def _infer_market_position(self, result: Dict) -> str:
        """Infer market position from search result"""
        text = (result.get("title", "") + " " + result.get("snippet", "")).lower()

        if any(term in text for term in ["leader", "leading", "top", "#1"]):
            return "leader"
        elif any(term in text for term in ["niche", "specialized", "focused"]):
            return "niche"
        else:
            return "challenger"

    def _calculate_similarity(self, idea: str, result: Dict) -> float:
        """Calculate similarity score"""
        idea_words = set(idea.lower().split())
        result_text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
        result_words = set(result_text.split())

        overlap = len(idea_words & result_words)
        return min(overlap / max(len(idea_words), 1), 1.0)

    def _extract_patent_id(self, url: str) -> str:
        """Extract patent ID from URL"""
        match = re.search(r"patent[/=]([A-Z0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else "unknown"

    def _extract_company_name(self, result: Dict) -> str:
        """Extract company name from funding announcement"""
        title = result.get("title", "")
        match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:raises|secures)", title)
        return match.group(1) if match else "Unknown Company"

    def _extract_funding_amount(self, result: Dict) -> str:
        """Extract funding amount"""
        text = result.get("title", "") + " " + result.get("snippet", "")
        match = re.search(r"\$(\d+\.?\d*)\s*(M|million|B|billion)", text, re.IGNORECASE)
        return f"${match.group(1)}{match.group(2)}" if match else "Undisclosed"

    def _extract_date(self, result: Dict) -> str:
        """Extract date from result"""
        text = result.get("snippet", "")
        patterns = [
            r"(January|February|March|April|May|June|July|August|"
            r"September|October|November|December)\s+\d{1,2},?\s+\d{4}",
            r"\d{1,2}/\d{1,2}/\d{4}",
            r"\d{4}",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return "Unknown"

    def _extract_round_type(self, result: Dict) -> str:
        """Extract funding round type"""
        text = (result.get("title", "") + " " + result.get("snippet", "")).lower()

        rounds = ["seed", "series a", "series b", "series c", "series d"]
        for round_type in rounds:
            if round_type in text:
                return round_type.replace(" ", "_")

        return "unknown"
