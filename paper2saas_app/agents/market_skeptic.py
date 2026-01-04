from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.firecrawl import FirecrawlTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import MARKET_SKEPTIC_INSTRUCTIONS

market_skeptic = Agent(
    name="MarketSkeptic",
    model=AgentConfig.MARKET_SKEPTIC_MODEL,
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    # reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    stream_intermediate_steps=False,
    instructions=MARKET_SKEPTIC_INSTRUCTIONS,
    markdown=True,
)
