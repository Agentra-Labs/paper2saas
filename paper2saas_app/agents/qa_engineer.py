from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import get_mistral_model, shared_db
from paper2saas_app.prompts.implementation_agents import QA_ENGINEER_INSTRUCTIONS

qa_engineer = Agent(
    name="QAEngineer",
    role="Design comprehensive testing strategies for SaaS applications",
    model=get_mistral_model(AgentConfig.QA_MODEL),
    tools=[
        ReasoningTools(add_instructions=True),
    ],
    db=shared_db,
    reasoning=False,
    stream_intermediate_steps=False,
    instructions=QA_ENGINEER_INSTRUCTIONS,
    markdown=True,
    tool_call_limit=2,
)
