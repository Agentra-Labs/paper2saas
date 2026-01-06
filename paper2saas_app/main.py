from agno.os import AgentOS

from .agents.paper_analyzer import paper_analyzer
from .agents.market_researcher import market_researcher
from .agents.idea_generator import idea_generator
from .agents.validation_researcher import validation_researcher
from .agents.strategic_advisor import strategic_advisor
from .agents.report_generator import report_generator
from .agents.product_engineer import product_engineer
from .agents.fact_checker import fact_checker
from .agents.devils_advocate import devils_advocate
from .agents.market_skeptic import market_skeptic

# Implementation Team Agents
from .agents.code_architect import code_architect
from .agents.fullstack_engineer import fullstack_engineer
from .agents.deployment_specialist import deployment_specialist
from .agents.qa_engineer import qa_engineer

from .teams.paper2saas import paper2saas_team
from .teams.roaster import idea_roaster_team
from .teams.implementation import implementation_team
from .config import AgentConfig

p2s_os = AgentOS(
    name="p2s-os",
    description="Turns academic papers into battle-tested SaaS opportunities with production-ready implementation",
    agents=[
        paper_analyzer,
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
        product_engineer,
        fact_checker,
        devils_advocate,
        market_skeptic,
        # Implementation Team Agents
        code_architect,
        fullstack_engineer,
        deployment_specialist,
        qa_engineer,
    ],
    teams=[
        paper2saas_team,     # Main flow: Paper analysis -> SaaS ideas
        idea_roaster_team,   # Critique: Stress-test ideas
        implementation_team, # Build: Production-ready code
    ],
    tracing=False,
)

app = p2s_os.get_app()

if __name__ == "__main__":
    p2s_os.serve(app="paper2saas_app.main:app", reload=True)
