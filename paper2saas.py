import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Agno Imports
from agno.agent import Agent
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput
from agno.db.sqlite import SqliteDb  # ← Use sync DB to avoid async errors
from agno.tools.reasoning import ReasoningTools
from agno.tools.workflow import WorkflowTools
from agno.tools.arxiv import ArxivTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.baidusearch import BaiduSearchTools

load_dotenv()

# Environment setup
os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY", "")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

# --- INPUT SCHEMA ---
class Paper2SaaSInput(BaseModel):
    """Input schema for the Paper2SaaS workflow."""
    arxiv_id: str = Field(..., description="The arXiv paper ID to analyze (e.g., '2401.00001')")


# --- AGENTS ---

paper_analyzer = Agent(
    name="PaperAnalyzer",
    model="mistral:mistral-large-latest",
    tools=[
        ArxivTools(),
        ReasoningTools(add_instructions=True),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True)
    ],
    instructions="""
You are an expert AI researcher tasked with analyzing a specific arXiv paper.

CRITICAL RULES:
- Always use ArxivTools.search_arxiv() with the exact provided arXiv ID.
- Never hallucinate or analyze a different paper.
- If the paper cannot be found, clearly state: "Paper not found for arXiv ID: {id}"

Required output format:
## Paper Title & ID
- Title: ...
- ArXiv ID: ...
- Authors: ...

## Executive Summary
[2-3 sentences]

## Core Technical Innovations
- ...

## Technical Architecture
[Key methods and design]

## Limitations & Constraints
- ...

## Potential Real-World Applications
- ...

## Key Results/Metrics
[If available]
""",
    markdown=True,
)

market_researcher = Agent(
    name="MarketResearcher",
    model="mistral:mistral-small-latest",
    tools=[HackerNewsTools(), WebsiteTools(), BaiduSearchTools()],
    instructions="""
You are a market intelligence expert in AI/ML and SaaS tools.

Research current pain points and opportunities in:
- Fine-tuning & model customization
- Deployment & serving
- Data labeling & preparation
- Cost and pricing of AI tools
- ML infrastructure & observability

Output format:
## Market Signals
- **Signal 1**: [Description + source/link]

## Key Pain Points
- **Pain Point 1**: [Who experiences it, evidence]

## Opportunity Areas
- **Area 1**: [Emerging need + indicators]
""",
    markdown=True,
)

idea_generator = Agent(
    name="IdeaGenerator",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    instructions="""
You are a world-class product strategist.

Using the paper analysis and market research provided, generate 7–10 SaaS product ideas that:
- Directly build on the paper's technical innovations
- Solve real, validated market pain points
- Are feasible for a small team
- Can generate revenue within 6 months

For each idea:
### Idea #X: [Catchy Name]
**Core Concept**: [1-2 sentences]
**Target Market**: [Segment + size estimate]
**Value Proposition**: [Why users pay]
**Technical Approach**: [How paper's tech enables it]
**Competitive Moat**: [Defensibility]
**Revenue Model**: [Subscription / usage / etc.]
**Implementation Complexity**: [Low/Medium/High] – [reason]
**MVP Features**: [3-4 bullet points]

Rank ideas by: Market demand (40%), Technical feasibility (30%), Revenue potential (30%).
""",
    markdown=True,
)

validation_researcher = Agent(
    name="ValidationResearcher",
    model="mistral:mistral-large-latest",
    tools=[FirecrawlTools(enable_search=True, enable_scrape=True), HackerNewsTools(), WebsiteTools()],
    instructions="""
Validate the TOP 3 ranked ideas with rigorous research.

For each idea:
## Idea: [Name + Core Concept]

### Market Validation
- **Demand Evidence**: [Searches, posts, requests found]
- **Market Size**: [Estimates]
- **Growth Indicators**: [Trends]

### Competitive Landscape
- **Direct Competitors**: [Name, URL, pricing]
- **Indirect Solutions**: [Alternatives]
- **Market Gaps**: [Unmet needs]

### Technical Validation
- **Implementation Risks**: [...]
- **Required Expertise**: [...]

### Go-to-Market
- **Early Adopters**: [Communities/companies]
- **Distribution Channels**: [...]
- **Pricing Benchmark**: [...]
""",
    markdown=True,
)

strategic_advisor = Agent(
    name="StrategicAdvisor",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    instructions="""
Perform a critical evaluation of each validated idea.

For each:
## Idea: [Name]

### SWOT Analysis
**Strengths**: ...
**Weaknesses**: ...
**Opportunities**: ...
**Threats**: ...

### Viability Score
- Market Fit: [1-10]
- Technical Feasibility: [1-10]
- Business Model: [1-10]
- Overall: [Average]

### Recommendation
**[PROCEED / PIVOT / PASS]**

**Reasoning**: [Detailed]
**Next Steps** (if PROCEED): 3 immediate actions
**Pivot Suggestions** (if PIVOT)
**Why Not** (if PASS)

Only recommend PROCEED if overall ≥ 7.5 and no fatal flaws.
""",
    markdown=True,
)

report_generator = Agent(
    name="ReportGenerator",
    model="mistral:mistral-large-latest",
    instructions="""
Create a professional executive report synthesizing all prior work.

# Paper-to-SaaS Opportunity Report

## Executive Summary
**Paper**: [Title + arXiv ID]
**Core Innovation**: [1 sentence]
**Market Gap**: [1 sentence]
**Top Recommendation**: [Idea name + value prop]
**Confidence**: [High/Medium/Low]

## Technical Summary
...

## Market Analysis Summary
...

## Top Recommendations
### Primary: [Name + details]
### Alternative: [Name + details]

## Implementation Roadmap
### Week 1-2: ...
### Week 3-4: ...
### Week 5-6: MVP Launch

## Success Metrics
- Month 1: ...
- Month 3: ...
- Month 6: ...

## Risk Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| ...  | ...    | ...        |

## Immediate Next Steps
1. ...
2. ...
3. ...

---
*Generated on January 03, 2026*
""",
    markdown=True,
)


# --- HELPER ---
def combine_research(step_input: StepInput) -> StepOutput:
    paper = step_input.get_step_content("analyze_paper") or "No paper analysis available."
    market = step_input.get_step_content("research_market") or "No market research available."

    combined = f"""
# Combined Research Context

## Paper Analysis
{paper}

## Market Research
{market}

## Next Step
Generate SaaS ideas that apply the paper's innovations to solve these market problems.
"""
    return StepOutput(step_name="combine_research", content=combined, success=True)


# --- WORKFLOW ---
paper2saas_workflow = Workflow(
    id="paper2saas",
    name="Paper2SaaS Discovery Engine",
    description="Turn any arXiv paper into validated SaaS opportunities",
    input_schema=Paper2SaaSInput,
    db=SqliteDb(db_file="tmp/paper2saas.db"),  # ← Sync DB = no async errors
    steps=[
        Parallel(
            Step(name="analyze_paper", agent=paper_analyzer),
            Step(name="research_market", agent=market_researcher),
            name="initial_research",
        ),
        Step(name="combine_research", executor=combine_research),
        Step(name="generate_ideas", agent=idea_generator),
        Step(name="validate_ideas", agent=validation_researcher),
        Step(name="advise", agent=strategic_advisor),
        Step(name="generate_report", agent=report_generator),
    ],
    store_events=True,
)


# --- MAIN ENTRYPOINT AGENT ---
workflow_agent = Agent(
    name="Paper2SaaS",
    model="mistral:mistral-large-latest",
    tools=[WorkflowTools(workflow=paper2saas_workflow, add_instructions=True)],
    instructions="""
You are Paper2SaaS — an AI system that transforms cutting-edge research papers into actionable, validated SaaS business opportunities.

When the user provides an arXiv ID (e.g., 2401.00001, 2511.13646, or a full URL), immediately run the 'paper2saas' workflow with that ID.

Extract the ID cleanly and pass it as structured input. Do not ask for confirmation — just execute.
""",
    markdown=True,
)