from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.product import PRODUCT_ENGINEER_INSTRUCTIONS
from paper2saas.tools.optional import get_optional_tools

# Base tools + optional (FirecrawlTools, BaiduSearchTools)
_tools = [
    WebsiteTools(),
    HackerNewsTools(),
] + get_optional_tools()

product_engineer = create_agent(
    name="Product Engineer",
    instructions=PRODUCT_ENGINEER_INSTRUCTIONS,
    tools=_tools,
    model_id=AgentConfig.LARGE_MODEL,
)
