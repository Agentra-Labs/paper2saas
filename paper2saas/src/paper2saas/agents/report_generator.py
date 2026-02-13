from agno.agent import Agent

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.reporting import REPORT_GENERATOR_INSTRUCTIONS

report_generator = create_agent(
    name="Report Generator",
    model_id=AgentConfig.SMALL_MODEL,  # Keep SMALL - just formatting
    instructions=REPORT_GENERATOR_INSTRUCTIONS,
)
