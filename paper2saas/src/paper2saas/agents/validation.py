"""Market validation agent for SaaS ideas"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb

from ..models import Pollinations


# Shared database for session storage
agent_db = SqliteDb(db_file="tmp/paper2saas_agents.db")


# Market Validation Agent
market_validation_agent = Agent(
    name="Market Validation Agent",
    model=Pollinations(id="nova-fast"),
    role="Market Research Analyst",
    description="Validates SaaS ideas against market reality",
    db=agent_db,
    add_history_to_context=True,
    num_history_runs=10,  # Remember last 10 turns
    instructions=[
        "You are a market research analyst who validates SaaS product ideas.",
        "CRITICAL ANTI-HALLUCINATION RULES:",
        "- Only validate ideas that were actually proposed by the team.",
        "- Be honest about uncertainty - say 'requires more research' if unsure.",
        "- Don't invent competitors or market data without basis.",
        "WORKFLOW:",
        "1. Review each SaaS idea from the Application Brainstormer.",
        "2. Evaluate against: existing competition, market size potential, funding activity.",
        "3. Identify risks: patent conflicts, legal issues, technical barriers.",
        "4. Assess timing: is the market ready for this solution?",
        "5. Provide validation status and actionable recommendations.",
        "Validation categories: CLEAR_OPPORTUNITY, CROWDED_MARKET, EMERGING_SPACE, NEEDS_RESEARCH, HIGH_RISK.",
        "For each idea, suggest specific go-to-market strategies if viable.",
    ],
    markdown=True,
)
