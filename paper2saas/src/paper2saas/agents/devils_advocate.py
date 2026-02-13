from agno.agent import Agent
from agno.tools.website import WebsiteTools

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.ideation import DEVILS_ADVOCATE_INSTRUCTIONS
from paper2saas.tools.optional import get_firecrawl_tools

# Base tools + optional FirecrawlTools
_tools = [WebsiteTools()]
if fc := get_firecrawl_tools():
    _tools.append(fc)

devils_advocate = create_agent(
    name="Devil's Advocate",
    model_id=AgentConfig.DEVILS_ADVOCATE_MODEL,
    tools=_tools,
    instructions=DEVILS_ADVOCATE_INSTRUCTIONS,
    references_format="yaml",
)
