from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.tools.website import WebsiteTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import get_mistral_model, shared_db
from paper2saas_app.prompts.implementation_agents import CODE_ARCHITECT_INSTRUCTIONS

code_architect = Agent(
    name="CodeArchitect",
    role="Design production-ready system architectures for SaaS applications",
    model=get_mistral_model(AgentConfig.ARCHITECT_MODEL),
    tools=[
        ReasoningTools(add_instructions=True),
        WebsiteTools(),
    ],
    db=shared_db,
    reasoning=False,
    stream_intermediate_steps=False,
    instructions=CODE_ARCHITECT_INSTRUCTIONS,
    markdown=True,
    tool_call_limit=3,
)
