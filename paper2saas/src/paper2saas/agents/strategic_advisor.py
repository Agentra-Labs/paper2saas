from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.ideation import STRATEGIC_ADVISOR_INSTRUCTIONS

strategic_advisor = create_agent(
    name="Strategic Advisor",
    model_id=AgentConfig.STRATEGIC_ADVISOR_MODEL,
    tools=[ReasoningTools()],
    # reasoning=True, # Commented out in original
    instructions=STRATEGIC_ADVISOR_INSTRUCTIONS,
)
