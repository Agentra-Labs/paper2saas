from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.market import MARKET_RESEARCHER_INSTRUCTIONS
from paper2saas.tools.optional import get_optional_tools
from paper2saas.knowledge import research_knowledge

# Base tools + optional (FirecrawlTools, BaiduSearchTools)
_tools = [
    HackerNewsTools(),
    WebsiteTools(),
] + get_optional_tools()

market_researcher = create_agent(
    name="Market Researcher",
    instructions=MARKET_RESEARCHER_INSTRUCTIONS,
    tools=_tools,
    model_id=AgentConfig.MARKET_RESEARCHER_MODEL,
    knowledge=research_knowledge,  # Shared knowledge base for cross-session access
    search_knowledge=True,  # Enable automatic knowledge search
)
