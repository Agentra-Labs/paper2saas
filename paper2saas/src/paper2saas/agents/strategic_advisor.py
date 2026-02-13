from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.ideation import STRATEGIC_ADVISOR_INSTRUCTIONS

strategic_advisor = create_agent(
    name="Strategic Advisor",
    model_id=AgentConfig.STRATEGIC_ADVISOR_MODEL,  # Keep LARGE for quality scoring
    tools=[],  # Removed ReasoningTools to save calls
    instructions=STRATEGIC_ADVISOR_INSTRUCTIONS,
)
