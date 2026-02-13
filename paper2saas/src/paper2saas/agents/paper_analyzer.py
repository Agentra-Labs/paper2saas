from agno.agent import Agent
from agno.tools.arxiv import ArxivTools
from agno.tools.website import WebsiteTools

from paper2saas.agent_config import AgentConfig
from paper2saas.agents.factory import create_agent
from paper2saas.prompts.research import PAPER_ANALYZER_INSTRUCTIONS
from paper2saas.tools.optional import get_optional_tools
from paper2saas.tools.semantic_scholar import SemanticScholarTools

# Base tools + optional (FirecrawlTools, BaiduSearchTools)
_tools = [
    ArxivTools(),
    SemanticScholarTools(),
    WebsiteTools(),
] + get_optional_tools()

paper_analyzer = create_agent(
    name="Paper Analyzer",
    instructions=PAPER_ANALYZER_INSTRUCTIONS,
    tools=_tools,
    model_id=AgentConfig.LARGE_MODEL,  # Keep LARGE for quality
    reasoning=False,
    tool_call_limit=3,  # Reduced from 4 to 3 (modest reduction)
)
