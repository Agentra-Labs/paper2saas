import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Agno Imports
from agno.agent import Agent
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput
from agno.db.sqlite import AsyncSqliteDb
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

# 1. Paper Analyzer
paper_analyzer = Agent(
    name="PaperAnalyzer",
    model="mistral:mistral-large-latest",
    tools=[ArxivTools(), ReasoningTools(add_instructions=True)],
    instructions="""
    You are an expert AI researcher. Your task is to analyze the specific arXiv paper provided.

    CRITICAL:
    - Use ArxivTools.search_arxiv() with the given arXiv ID to fetch the exact paper.
    - Do NOT hallucinate or analyze any other paper.
    - If the paper cannot be found, report it clearly.

    Output structure:
    ## Paper Title & ID
    - Title: [Actual title]
    - ArXiv ID: [Given ID]
    - Authors: [List]

    ## Executive Summary
    [2-3 sentences]

    ## Core Technical Innovations
    - [Innovation 1]
    - [Innovation 2]
    - [Innovation 3]

    ## Technical Architecture
    [Key details]

    ## Limitations & Constraints
    - [Limitation 1]
    - [Limitation 2]

    ## Potential Real-World Applications
    - [Application 1]
    - [Application 2]
    - [Application 3]

    ## Key Results/Metrics
    [Metrics if available]
    """,
    markdown=True,
)

# 2. Market Researcher
market_researcher = Agent(
    name="MarketResearcher",
    model="mistral:mistral-small-latest",
    tools=[HackerNewsTools(), WebsiteTools(), BaiduSearchTools()],
    instructions="""
    You are a market research expert in AI/ML/SaaS.

    Search for recent discussions on:
    - AI tool frustrations
    - Fine-tuning/deployment/data challenges
    - ML infrastructure pain points
    - Pricing complaints

    Output:
    ## Market Signals
    - **Signal 1**: [Description + source]
    - **Signal 2**: ...

    ## Key Pain Points
    - **Pain Point 1**: [Who, why, evidence]
    - **Pain Point 2**: ...

    ## Opportunity Areas
    - **Area 1**: [Description]
    - **Area 2**: ...

    Focus on recent data.
    """,
    markdown=True,
)

# 3. Idea Generator
idea_generator = Agent(
    name="IdeaGenerator",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    instructions="""
    You are a product strategist. Using the paper analysis and market research:

    Generate 7-10 SaaS ideas that:
    - Directly leverage the paper's innovations
    - Solve specific market pain points
    - Are revenue-viable in 6 months
    - Feasible for a small team

    For each idea:
    ### Idea #X: [Name]
    **Core Concept**: ...
    **Target Market**: ...
    **Value Proposition**: ...
    **Technical Approach**: ...
    **Competitive Moat**: ...
    **Revenue Model**: ...
    **Implementation Complexity**: [Low/Medium/High] - [Why]
    **MVP Features**: [3-4 features]

    Rank by market demand (40%), feasibility (30%), revenue (30%).
    """,
    markdown=True,
)

# 4. Validation Researcher
validation_researcher = Agent(
    name="ValidationResearcher",
    model="mistral:mistral-large-latest",
    tools=[FirecrawlTools(enable_search=True, enable_scrape=True), HackerNewsTools(), WebsiteTools()],
    instructions="""
    You are a due diligence expert. Validate the TOP 3 ranked ideas.

    For each:
    ## Idea: [Name + Concept]

    ### Market Validation
    - **Demand Evidence**: ...
    - **Market Size**: ...
    - **Growth Indicators**: ...

    ### Competitive Landscape
    - **Direct Competitors**: [Name, URL, features, pricing]
    - **Indirect Solutions**: ...
    - **Market Gaps**: ...

    ### Technical Validation
    - **Implementation Examples**: ...
    - **Technical Risks**: ...
    - **Required Expertise**: ...

    ### Go-to-Market
    - **Early Adopters**: ...
    - **Distribution Channels**: ...
    - **Pricing Benchmark**: ...

    ### Risk Assessment
    - **Primary Risk**: ...
    - **Mitigation**: ...
    """,
    markdown=True,
)

# 5. Strategic Advisor
strategic_advisor = Agent(
    name="StrategicAdvisor",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    instructions="""
    You are a startup advisor. For each validated idea:

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
    **Reasoning**: ...
    **If PROCEED**: Next 3 steps
    **If PIVOT**: Suggested changes
    **If PASS**: Why not

    Only PROCEED if overall ≥7 and no critical blockers.
    """,
    markdown=True,
)

# 6. Report Generator
report_generator = Agent(
    name="ReportGenerator",
    model="mistral:mistral-large-latest",
    instructions="""
    Synthesize into a professional report.

    # Paper-to-SaaS Opportunity Report
    ## Executive Summary
    ...

    ## Technical Innovation Summary
    ...

    ## Market Analysis Summary
    ...

    ## Top SaaS Recommendations
    ### 🥇 Primary: ...
    ### 🥈 Alternative: ...

    ## Implementation Roadmap
    ...

    ## Success Metrics
    ...

    ## Risk Mitigation
    | Risk | Impact | Mitigation |
    |------|--------|------------|
    ...

    ## Immediate Next Steps
    ...
    """,
    markdown=True,
)

# --- HELPER EXECUTORS ---

def combine_research(step_input: StepInput) -> StepOutput:
    paper = step_input.get_step_content("analyze_paper") or "No paper analysis"
    market = step_input.get_step_content("research_market") or "No market research"

    combined = f"""
# Combined Research

## 📄 Paper Analysis
{paper}

## 📊 Market Research
{market}

## 🎯 Goal
Generate SaaS ideas bridging the paper's innovations with market needs.
    """
    return StepOutput(step_name="combine_research", content=combined, success=True)

# --- WORKFLOW ---

paper2saas_workflow = Workflow(
    id="paper2saas",
    name="Paper2SaaS Discovery Engine",
    description="Analyze an arXiv paper for SaaS opportunities",
    input_schema=Paper2SaaSInput,
    db=AsyncSqliteDb(db_file="tmp/paper2saas.db"),
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

# --- WORKFLOW AGENT (for direct chat access) ---

workflow_agent = Agent(
    name="Paper2SaaS",
    model="mistral:mistral-large-latest",
    tools=[WorkflowTools(workflow=paper2saas_workflow)],
    instructions="You are the entrypoint for the Paper2SaaS system. Run the workflow with the provided arXiv ID.",
    markdown=True,
)