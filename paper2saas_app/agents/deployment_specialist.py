from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import get_mistral_model, shared_db
from paper2saas_app.prompts.implementation_agents import DEPLOYMENT_SPECIALIST_INSTRUCTIONS

deployment_specialist = Agent(
    name="DeploymentSpecialist",
    role="Create deployment configurations for production environments",
    model=get_mistral_model(AgentConfig.DEPLOYMENT_MODEL),
    tools=[
        ReasoningTools(add_instructions=True),
    ],
    db=shared_db,
    reasoning=False,
    stream_intermediate_steps=False,
    instructions=DEPLOYMENT_SPECIALIST_INSTRUCTIONS,
    markdown=True,
    tool_call_limit=2,
)
