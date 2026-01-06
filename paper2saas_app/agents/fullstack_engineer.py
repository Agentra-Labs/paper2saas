from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.tools.website import WebsiteTools
from agno.tools.firecrawl import FirecrawlTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import get_mistral_model, shared_db
from paper2saas_app.prompts.implementation_agents import FULLSTACK_ENGINEER_INSTRUCTIONS

fullstack_engineer = Agent(
    name="FullStackEngineer",
    role="Generate production-ready code for SaaS applications",
    model=get_mistral_model(AgentConfig.ENGINEER_MODEL),
    tools=[
        ReasoningTools(add_instructions=True),
        WebsiteTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    db=shared_db,
    reasoning=False,
    stream_intermediate_steps=False,
    instructions=FULLSTACK_ENGINEER_INSTRUCTIONS,
    markdown=True,
    tool_call_limit=5,
)
