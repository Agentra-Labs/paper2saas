"""Agent definitions for Paper2SaaS.

Contains specialized AI agents for the paper-to-SaaS pipeline:
- Analysis: paper_analyzer, market_researcher
- Generation: idea_generator, validation_researcher
- Evaluation: strategic_advisor, fact_checker, product_engineer
- Output: report_generator
- Critique: devils_advocate, market_skeptic
"""

from .paper_analyzer import paper_analyzer
from .market_researcher import market_researcher
from .idea_generator import idea_generator
from .validation_researcher import validation_researcher
from .strategic_advisor import strategic_advisor
from .product_engineer import product_engineer
from .fact_checker import fact_checker
from .report_generator import report_generator
from .devils_advocate import devils_advocate
from .market_skeptic import market_skeptic

__all__ = [
    "paper_analyzer",
    "market_researcher",
    "idea_generator",
    "validation_researcher",
    "strategic_advisor",
    "product_engineer",
    "fact_checker",
    "report_generator",
    "devils_advocate",
    "market_skeptic",
]
