"""
Application Ideation Workflow
Multi-agent pipeline that connects research paper ideas to real-world problems

Architecture:
- Phase 1: Parallel Research (3 agents gather raw material)
- Phase 2: Iterative Ideation Loop (progressively creative thinking)
- Phase 3: Cross-Domain Synthesis (connect dots, rank ideas)
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.tools.arxiv import ArxivTools
from agno.tools.hackernews import HackerNewsTools
from agno.workflow import Workflow, Step
from agno.workflow.parallel import Parallel
from agno.workflow.loop import Loop

from ..models import Pollinations
from ..tools import SemanticScholarTools
from ..knowledge import research_knowledge


# Shared database for session storage
agent_db = SqliteDb(db_file="tmp/paper2saas_agents.db")


# =============================================================================
# PHASE 1: Parallel Research Agents
# =============================================================================

paper_analyzer = Agent(
    name="Paper Analyzer",
    model=Pollinations(id="nova-fast"),
    role="Technical Extractor",
    description="Extracts core technique and capabilities from research papers",
    tools=[ArxivTools(), SemanticScholarTools()],
    knowledge=research_knowledge,
    search_knowledge=True,
    db=agent_db,
    instructions=[
        "Read the paper and extract these specific things:",
        "",
        "1. CORE TECHNIQUE: What does this paper actually do? (one sentence)",
        "2. KEY CAPABILITIES: What becomes possible with this? (bullet list)",
        "3. LIMITATIONS: What can't it do? What does it require? (bullet list)",
        "4. MATURITY: Is this theoretical, prototype, or production-ready?",
        "",
        "Be specific. Quote actual numbers, methods, or results from the paper.",
        "If you can't find the paper, say so - don't make things up.",
    ],
    markdown=True,
)

domain_explorer = Agent(
    name="Domain Explorer",
    model=Pollinations(id="nova-fast"),
    role="Field Mapper",
    description="Finds domains and industries where techniques could apply",
    tools=[SemanticScholarTools()],
    db=agent_db,
    instructions=[
        "Given the paper's technique, find where it could be useful:",
        "",
        "1. Search for papers that cite similar work - which fields are they in?",
        "2. What adjacent domains face similar problems?",
        "3. What industries have the problem this technique solves?",
        "",
        "Be specific: 'radiologists at hospitals' not 'healthcare'",
        "Search broadly - look beyond the obvious applications.",
        "List at least 5 different domains/industries.",
    ],
    markdown=True,
)

trend_scout = Agent(
    name="Trend Scout",
    model=Pollinations(id="nova-fast"),
    role="Community Signal Detector",
    description="Finds community discussions and pain points related to the topic",
    tools=[HackerNewsTools()],
    db=agent_db,
    instructions=[
        "Search HackerNews to find real-world signals:",
        "",
        "1. Are developers discussing related technology or problems?",
        "2. Look for: 'I wish X existed' or 'Why doesn't Y work?' threads",
        "3. What projects are people building in this space?",
        "4. What pain points do practitioners mention?",
        "",
        "Report what you actually find. If there's no discussion, say so.",
        "Include links to relevant threads when you find them.",
    ],
    markdown=True,
)


# =============================================================================
# PHASE 2: Ideation Agent (runs in loop)
# =============================================================================

idea_generator = Agent(
    name="Idea Generator",
    model=Pollinations(id="nova-fast"),
    role="Application Ideator",
    description="Brainstorms applications connecting research to real-world problems",
    knowledge=research_knowledge,
    search_knowledge=True,
    db=agent_db,
    instructions=[
        "Using the research gathered, brainstorm specific applications.",
        "",
        "FOR EACH IDEA, PROVIDE:",
        "- **Problem**: What specific real-world problem does this address?",
        "- **Who needs it**: Exact roles/people (not 'enterprises' or 'businesses')",
        "- **How it works**: How does the paper's technique solve this?",
        "- **What's missing**: What needs to happen before this is practical?",
        "",
        "ITERATE CREATIVELY:",
        "- First pass: Start with obvious applications mentioned in the paper",
        "- Second pass: Find non-obvious applications in adjacent domains",
        "- Third pass: Make wild cross-domain connections",
        "",
        "QUALITY RULES:",
        "- Be concrete: 'Automate legal contract review' not 'transform industries'",
        "- Name specific job roles: 'immigration lawyers' not 'legal sector'",
        "- Explain the mechanism: how does the technique actually apply?",
        "- Acknowledge gaps honestly",
        "",
        "Generate at least 3 distinct ideas per iteration.",
    ],
    markdown=True,
)


# =============================================================================
# PHASE 3: Cross-Domain Connector
# =============================================================================

connector_agent = Agent(
    name="Cross-Domain Connector",
    model=Pollinations(id="nova-fast"),
    role="Idea Synthesizer",
    description="Connects ideas across domains and ranks by novelty and feasibility",
    db=agent_db,
    instructions=[
        "Review all generated ideas and synthesize:",
        "",
        "1. FIND CONNECTIONS: What unexpected links exist between domains?",
        "   - Could an idea from domain A work in domain B?",
        "   - What common patterns appear across different applications?",
        "",
        "2. FILTER FOR NOVELTY: Which ideas are truly new?",
        "   - Does this already exist? (be honest)",
        "   - What makes this different from existing solutions?",
        "",
        "3. RANK TOP 5 IDEAS by: novelty × feasibility × impact",
        "   For each, explain:",
        "   - Why it's novel",
        "   - Why it's feasible (or what makes it hard)",
        "   - What impact it could have",
        "",
        "Be ruthless. Cut ideas that are vague or already exist.",
    ],
    markdown=True,
)


# =============================================================================
# BUILD THE WORKFLOW
# =============================================================================

# Create steps
analyze_paper_step = Step(
    name="Analyze Paper",
    agent=paper_analyzer,
    description="Extract the core technique, capabilities, and limitations from the research paper.",
)

explore_domains_step = Step(
    name="Explore Domains",
    agent=domain_explorer,
    description="Find domains and industries where this technique could be applied.",
)

scout_trends_step = Step(
    name="Scout Trends",
    agent=trend_scout,
    description="Search HackerNews for related discussions, projects, and pain points.",
)

generate_ideas_step = Step(
    name="Generate Ideas",
    agent=idea_generator,
    description="Brainstorm specific applications that connect the research to real-world problems.",
)

connect_and_rank_step = Step(
    name="Connect & Rank",
    agent=connector_agent,
    description="Synthesize all ideas, find cross-domain connections, and rank the top 5.",
)


# Assemble the workflow
ideation_workflow = Workflow(
    name="Application Ideation Pipeline",
    description="Transform research papers into ranked, substantive application ideas",
    db=agent_db,
    session_state={
        "paper_analysis": None,
        "domains": [],
        "trends": [],
        "ideas": [],
    },
    steps=[
        # Phase 1: Parallel research gathering
        Parallel(
            analyze_paper_step,
            explore_domains_step,
            scout_trends_step,
            name="Research Phase",
            description="Gather paper analysis, domain mapping, and community signals in parallel",
        ),
        # Phase 2: Iterative ideation
        Loop(
            steps=[generate_ideas_step],
            max_iterations=3,
            name="Ideation Loop",
            description="Generate ideas iteratively, getting more creative each round",
        ),
        # Phase 3: Synthesis and ranking
        connect_and_rank_step,
    ],
)
