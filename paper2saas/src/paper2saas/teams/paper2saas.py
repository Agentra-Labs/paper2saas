from agno.team import Team
import uuid

from paper2saas.agent_config import AgentConfig
from paper2saas.utils import (
    shared_db,
    logger,
    run_team_with_error_handling,
    arun_team_with_error_handling,
    validate_arxiv_id,
    get_mistral_model,
)
from paper2saas.prompts.agents import PAPER2SAAS_TEAM_INSTRUCTIONS

# Import agents
from paper2saas.agents.paper_analyzer import paper_analyzer
from paper2saas.agents.market_researcher import market_researcher
from paper2saas.agents.idea_generator import idea_generator
from paper2saas.agents.validation_researcher import validation_researcher
from paper2saas.agents.strategic_advisor import strategic_advisor
from paper2saas.agents.fact_checker import fact_checker
from paper2saas.agents.product_engineer import product_engineer
from paper2saas.agents.report_generator import report_generator

# --- OPTIMIZED FLAT TEAM (Minimized LLM Overhead) ---

paper2saas_team = Team(
    name="Paper2SaaS",
    role="High-efficiency paper-to-SaaS transformation pipeline",
    model=get_mistral_model(AgentConfig.LARGE_MODEL),
    instructions=PAPER2SAAS_TEAM_INSTRUCTIONS,
    members=[
        paper_analyzer,  # LARGE_MODEL: Technical extraction
        market_researcher,  # SMALL_MODEL: Data lookup
        fact_checker,  # SMALL_MODEL: Verification
        idea_generator,  # SMALL_MODEL: Synthesis
        validation_researcher,  # LARGE_MODEL: Competitive research
        strategic_advisor,  # LARGE_MODEL: Scoring
        product_engineer,  # LARGE_MODEL: Tech planning
        report_generator,  # SMALL_MODEL: Final formatting
    ],
    db=shared_db,
    store_events=AgentConfig.STORE_EVENTS,
    markdown=AgentConfig.ENABLE_MARKDOWN,
    show_members_responses=AgentConfig.SHOW_MEMBER_RESPONSES,
    add_datetime_to_context=True,
    # --- COST & PERFORMANCE OPTIMIZATION ---
    cache_session=True,  # In-memory hydration
    enable_user_memories=True,  # Persistent context
    delegate_to_all_members=True,  # Broadcast to all members simultaneously for parallel execution
    # Use smaller model for supervisor if possible, but LARGE is safer for complex delegation
)

logger.info(
    "Optimized Paper2SaaS team for minimal latency and cost (Flat structure + Model Tiering)"
)


def run_paper2saas(arxiv_id: str) -> dict:
    """
    Execute paper2saas_team with comprehensive error handling

    Args:
        arxiv_id: The arXiv paper ID to analyze

    Returns:
        dict with status, result/error, and metadata
    """
    # Validate input
    if not validate_arxiv_id(arxiv_id):
        logger.error(f"Invalid arXiv ID format: {arxiv_id}")
        return {
            "status": "error",
            "error": f"Invalid arXiv ID format: {arxiv_id}. Expected format: YYMM.NNNNN or YYMM.NNNNNvN",
            "arxiv_id": arxiv_id,
        }

    # Generate a unique session ID for this run to prevent context pollution
    session_id = str(uuid.uuid4())
    logger.info(f"Generated session ID: {session_id} for arXiv ID: {arxiv_id}")

    result = run_team_with_error_handling(
        team=paper2saas_team,
        input_text=f"Analyze arXiv paper {arxiv_id} and generate SaaS opportunities",
        log_start_msg=f"Starting paper2saas analysis for arXiv ID: {arxiv_id}",
        log_success_msg=f"Successfully completed analysis for {arxiv_id}",
        session_id=session_id,
    )

    # --- PERFORMANCE METRICS ---
    if result["status"] == "success":
        run_output = result["result"]
        metrics = {
            "total_tokens": getattr(run_output, "metrics", None)
            and getattr(run_output.metrics, "total_tokens", "N/A"),
            "execution_time": getattr(run_output, "metrics", None)
            and getattr(run_output.metrics, "time", "N/A"),
        }
        logger.info(f"Execution Metrics: {metrics}")
        result["metrics"] = metrics

    # Add arxiv_id to result
    result["arxiv_id"] = arxiv_id
    result["session_id"] = session_id
    return result


async def arun_paper2saas(arxiv_id: str) -> dict:
    """
    Async version for minimal latency - executes agents concurrently.

    Args:
        arxiv_id: The arXiv paper ID to analyze

    Returns:
        dict with status, result/error, and metadata
    """
    # Validate input
    if not validate_arxiv_id(arxiv_id):
        logger.error(f"Invalid arXiv ID format: {arxiv_id}")
        return {
            "status": "error",
            "error": f"Invalid arXiv ID format: {arxiv_id}. Expected format: YYMM.NNNNN or YYMM.NNNNNvN",
            "arxiv_id": arxiv_id,
        }

    # Generate a unique session ID for this run to prevent context pollution
    session_id = str(uuid.uuid4())
    logger.info(f"Generated session ID: {session_id} for arXiv ID: {arxiv_id} (async)")

    result = await arun_team_with_error_handling(
        team=paper2saas_team,
        input_text=f"Analyze arXiv paper {arxiv_id} and generate SaaS opportunities",
        log_start_msg=f"Starting async paper2saas analysis for arXiv ID: {arxiv_id}",
        log_success_msg=f"Successfully completed async analysis for {arxiv_id}",
        session_id=session_id,
    )

    # --- PERFORMANCE METRICS ---
    if result["status"] == "success":
        run_output = result["result"]
        metrics = {
            "total_tokens": getattr(run_output, "metrics", None)
            and getattr(run_output.metrics, "total_tokens", "N/A"),
            "execution_time": getattr(run_output, "metrics", None)
            and getattr(run_output.metrics, "time", "N/A"),
        }
        logger.info(f"Async Execution Metrics: {metrics}")
        result["metrics"] = metrics

    # Add arxiv_id to result
    result["arxiv_id"] = arxiv_id
    result["session_id"] = session_id
    return result
