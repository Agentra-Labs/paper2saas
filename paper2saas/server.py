"""
Paper2SaaS — AgentOS Server
Multi-agent pipeline: arXiv paper → validated SaaS opportunity report

Run: uv run python server.py
"""

from dotenv import load_dotenv

load_dotenv()

from agno.os import AgentOS

# Import all 10 agents
from paper2saas.agents import (
    paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    product_engineer,
    fact_checker,
    report_generator,
    devils_advocate,
    market_skeptic,
)

# Import both teams
from paper2saas.teams import paper2saas_team, idea_roaster_team

# Create AgentOS with all agents and both teams
agent_os = AgentOS(
    agents=[
        paper_analyzer,
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        product_engineer,
        fact_checker,
        report_generator,
        devils_advocate,
        market_skeptic,
    ],
    teams=[paper2saas_team, idea_roaster_team],
    name="Paper2SaaS",
    description="Transform arXiv papers into validated SaaS business opportunities",
)

# FastAPI app for uvicorn
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve("server:app", port=7777)
