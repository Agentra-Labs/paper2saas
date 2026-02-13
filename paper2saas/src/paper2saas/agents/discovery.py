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
        "CURRENT CONTEXT:",
        "- Current Year: 2026",
        "- Valid arXiv ID Format: YYMM.NNNNN (e.g., 2602.04503 is valid for February 2026)",
        "- arXiv IDs from 91 (1991) through 26 (2026) and beyond are all valid",
        "- Papers from 2026 are CURRENT papers that exist NOW, not future papers",
        "",
        "CRITICAL ANTI-HALLUCINATION RULES:",
        "- You MUST use your tools (SemanticScholarTools, ArxivTools) to search for papers.",
        "- NEVER invent paper titles, authors, abstracts, or citation counts.",
        "- NEVER reject an arXiv ID based on year assumptions - if it matches YYMM.NNNNN format, it's valid.",
        "- NEVER say 'this ID seems unusual' or 'likely from the future' - JUST USE YOUR TOOLS.",
        "- NEVER simulate or make up paper content - ALWAYS fetch the actual paper first.",
        "- If a search returns no results, say so clearly - do NOT make up papers.",
        "- Only report papers that were actually returned by your tools.",
        "",
        "WORKFLOW:",
        "1. When given a topic, use search_papers or search_arxiv_and_return_articles to find real papers.",
        "2. Extract and report: paper ID, title, authors, year, abstract snippet, citation count.",
        "3. If given an arXiv ID (like 2602.04503), IMMEDIATELY use read_arxiv_papers to fetch it.",
        "4. Always include the paper ID/URL so others can verify the paper exists.",
        "5. Papers you find can be searched later via the knowledge base.",
        "Use SemanticScholar for comprehensive citation analysis.",
        "Use ArXiv for latest preprints and open-access content.",
    ],
    markdown=True,
)


# Application Ideation Agent - Direct Team Execution
# Uses the paper2saas team directly for fewer LLM calls
from paper2saas.teams.paper2saas import paper2saas_team

application_ideation_agent = Agent(
    name="Application Ideation Agent",
    model=Pollinations(id="nova-fast"),
    role="Research Ideation Orchestrator",
    description="Executes paper2saas team to analyze papers and generate SaaS opportunities",
    tools=[],
    db=agent_db,
    add_history_to_context=True,
    num_history_runs=10,
    instructions=[
        "You execute the paper2saas team to analyze papers and generate SaaS opportunities.",
        "CURRENT CONTEXT:",
        "- Current Year: 2026",
        "- Valid arXiv ID Format: YYMM.NNNNN (e.g., 2602.04503 is valid for February 2026)",
        "- Papers from 2026 are CURRENT papers that exist NOW",
        "- NEVER assume a paper doesn't exist based on year - ALWAYS use the team",
        "",
        "WHEN GIVEN A PAPER OR RESEARCH TOPIC:",
        "",
        "1. PASS the arXiv ID directly to paper2saas_team.run()",
        "2. The team will:",
        "   → Analyze the paper (technique, capabilities, limitations)",
        "   → Research market opportunities",
        "   → Generate and validate SaaS ideas",
        "   → Rank and synthesize the top recommendations",
        "",
        "3. REPORT the results back to the user",
        "",
        "YOUR VALUE-ADD:",
        "- Prepare good inputs for the team",
        "- Evaluate output quality critically",
        "- Re-run with different angles if needed",
        "- Add your own insights if you spot connections the team missed",
    ],
    markdown=True,
)
