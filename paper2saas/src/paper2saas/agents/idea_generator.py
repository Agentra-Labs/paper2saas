from agno.agent import Agent

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.ideation import IDEA_GENERATOR_INSTRUCTIONS

idea_generator = create_agent(
    name="Idea Generator",
    instructions=IDEA_GENERATOR_INSTRUCTIONS,
    tools=[],
    model_id=AgentConfig.SMALL_MODEL,
)
