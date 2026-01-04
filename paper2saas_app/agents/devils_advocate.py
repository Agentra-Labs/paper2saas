from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.website import WebsiteTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import DEVILS_ADVOCATE_INSTRUCTIONS

devils_advocate = Agent(
    name="DevilsAdvocate",
    model=AgentConfig.DEVILS_ADVOCATE_MODEL,
    tools=[
        ReasoningTools(add_instructions=True),
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
    ],
    # reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    stream_intermediate_steps=False,
    instructions=DEVILS_ADVOCATE_INSTRUCTIONS,
    markdown=True,
)
