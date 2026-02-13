"""Tests for Paper2SaaS agent definitions and functionality."""

import pytest


class TestAgentDefinitions:
    """Tests for agent instantiation."""

    def test_paper_analyzer_exists(self):
        """paper_analyzer should be importable."""
        from paper2saas.agents import paper_analyzer

        assert paper_analyzer is not None
        assert paper_analyzer.name == "Paper Analyzer"

    def test_market_researcher_exists(self):
        """market_researcher should be importable."""
        from paper2saas.agents import market_researcher

        assert market_researcher is not None
        assert market_researcher.name == "Market Researcher"

    def test_idea_generator_exists(self):
        """idea_generator should be importable."""
        from paper2saas.agents import idea_generator

        assert idea_generator is not None
        assert idea_generator.name == "Idea Generator"

    def test_validation_researcher_exists(self):
        """validation_researcher should be importable."""
        from paper2saas.agents import validation_researcher

        assert validation_researcher is not None
        assert validation_researcher.name == "Validation Researcher"

    def test_strategic_advisor_exists(self):
        """strategic_advisor should be importable."""
        from paper2saas.agents import strategic_advisor

        assert strategic_advisor is not None
        assert strategic_advisor.name == "Strategic Advisor"

    def test_product_engineer_exists(self):
        """product_engineer should be importable."""
        from paper2saas.agents import product_engineer

        assert product_engineer is not None
        assert product_engineer.name == "Product Engineer"

    def test_fact_checker_exists(self):
        """fact_checker should be importable."""
        from paper2saas.agents import fact_checker

        assert fact_checker is not None
        assert fact_checker.name == "Fact Checker"

    def test_report_generator_exists(self):
        """report_generator should be importable."""
        from paper2saas.agents import report_generator

        assert report_generator is not None
        assert report_generator.name == "Report Generator"

    def test_devils_advocate_exists(self):
        """devils_advocate should be importable."""
        from paper2saas.agents import devils_advocate

        assert devils_advocate is not None
        assert devils_advocate.name == "Devil's Advocate"

    def test_market_skeptic_exists(self):
        """market_skeptic should be importable."""
        from paper2saas.agents import market_skeptic

        assert market_skeptic is not None
        assert market_skeptic.name == "Market Skeptic"


class TestAgentsHaveTools:
    """Tests for agent tool configuration."""

    def test_paper_analyzer_has_tools(self):
        """Paper Analyzer should have tools attached."""
        from paper2saas.agents import paper_analyzer

        assert hasattr(paper_analyzer, "tools")
        assert paper_analyzer.tools is not None
        assert len(paper_analyzer.tools) > 0

    def test_market_researcher_has_tools(self):
        """Market Researcher should have tools attached."""
        from paper2saas.agents import market_researcher

        assert hasattr(market_researcher, "tools")
        assert market_researcher.tools is not None
        assert len(market_researcher.tools) > 0


class TestAgentsHaveInstructions:
    """Tests for agent instruction configuration."""

    def test_paper_analyzer_has_instructions(self):
        """Paper Analyzer should have instructions defined."""
        from paper2saas.agents import paper_analyzer

        assert hasattr(paper_analyzer, "instructions")
        assert paper_analyzer.instructions is not None
        assert len(paper_analyzer.instructions) > 0

    def test_report_generator_has_instructions(self):
        """Report Generator should have instructions defined."""
        from paper2saas.agents import report_generator

        assert hasattr(report_generator, "instructions")
        assert report_generator.instructions is not None
        assert len(report_generator.instructions) > 0
