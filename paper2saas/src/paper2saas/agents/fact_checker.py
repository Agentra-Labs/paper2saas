from agno.agent import Agent

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.research import FACT_CHECKER_INSTRUCTIONS

fact_checker = create_agent(
    name="Fact Checker",
    model_id=AgentConfig.FACT_CHECKER_MODEL,
    tools=[],
    instructions=FACT_CHECKER_INSTRUCTIONS,
)
