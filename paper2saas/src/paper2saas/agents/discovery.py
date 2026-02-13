"""Paper discovery agents for research exploration"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.tools.arxiv import ArxivTools

from ..models import Pollinations
from ..tools import SemanticScholarTools
from ..knowledge import research_knowledge


# Shared database for session storage across all agents
agent_db = SqliteDb(db_file="tmp/paper2saas_agents.db")


# Paper Discovery Agent - finds research papers
paper_discovery_agent = Agent(
    name="Paper Discovery Agent",
    model=Pollinations(id="nova-fast"),
    role="Research Paper Finder",
    description="Discovers and analyzes academic papers for research insights",
    tools=[SemanticScholarTools(), ArxivTools()],
    db=agent_db,
    add_history_to_context=True,
    num_history_runs=10,  # Remember last 10 turns
    knowledge=research_knowledge,  # Shared knowledge base
    search_knowledge=True,
    instructions=[
        "You are a research discovery assistant specializing in finding academic papers.",
        "CRITICAL ANTI-HALLUCINATION RULES:",
        "- You MUST use your tools (SemanticScholarTools, ArxivTools) to search for papers.",
        "- NEVER invent paper titles, authors, abstracts, or citation counts.",
        "- If a search returns no results, say so clearly - do NOT make up papers.",
        "- Only report papers that were actually returned by your tools.",
        "WORKFLOW:",
        "1. When given a topic, use search_papers or search_arxiv_and_return_articles to find real papers.",
        "2. Extract and report: paper ID, title, authors, year, abstract snippet, citation count.",
        "3. If given an arXiv ID (like 2301.12345), use read_arxiv_papers to fetch the actual paper.",
        "4. Always include the paper ID/URL so others can verify the paper exists.",
        "5. Papers you find can be searched later via the knowledge base.",
        "Use SemanticScholar for comprehensive citation analysis.",
        "Use ArXiv for latest preprints and open-access content.",
    ],
    markdown=True,
)


# Application Ideation Agent - Workflow Orchestrator
# Uses the multi-agent ideation workflow to connect research to real-world problems
from agno.tools.workflow import WorkflowTools
from ..workflows.ideation_workflow import ideation_workflow

application_ideation_agent = Agent(
    name="Application Ideation Agent",
    model=Pollinations(id="nova-fast"),
    role="Research Ideation Orchestrator",
    description="Orchestrates a multi-agent workflow to connect research ideas to real-world applications",
    tools=[
        WorkflowTools(
            workflow=ideation_workflow,
            add_instructions=True,
            enable_think=True,
            enable_analyze=True,
        ),
    ],
    db=agent_db,
    add_history_to_context=True,
    num_history_runs=10,
    instructions=[
        "You orchestrate a powerful multi-agent ideation workflow.",
        "",
        "WHEN GIVEN A PAPER OR RESEARCH TOPIC:",
        "",
        "1. USE think() TO PLAN:",
        "   - What is the paper about?",
        "   - What should the workflow focus on?",
        "   - Any specific domains to explore?",
        "",
        "2. USE run_workflow() TO EXECUTE:",
        "   - Pass the paper ID, arXiv ID, or topic as input",
        "   - The workflow will:",
        "     → Analyze the paper (technique, capabilities, limitations)",
        "     → Explore relevant domains in parallel",
        "     → Scout HackerNews for community signals",
        "     → Generate ideas iteratively (obvious → non-obvious → cross-domain)",
        "     → Rank and synthesize the top 5 ideas",
        "",
        "3. USE analyze() TO EVALUATE:",
        "   - Are the results substantive and specific?",
        "   - Do the ideas have concrete problem statements?",
        "   - If results are weak, run again with refined focus",
        "",
        "YOUR VALUE-ADD:",
        "- Prepare good inputs for the workflow",
        "- Evaluate output quality critically",
        "- Re-run with different angles if needed",
        "- Add your own cross-domain insights if you spot connections the workflow missed",
    ],
    markdown=True,
)
