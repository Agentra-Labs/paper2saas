from agno.team import Team
import uuid

from paper2saas.agent_config import AgentConfig
from paper2saas.utils import shared_db, logger, run_team_with_error_handling, get_mistral_model
from paper2saas.prompts.agents import IDEA_ROASTER_TEAM_INSTRUCTIONS

# Import agents
from paper2saas.agents.devils_advocate import devils_advocate
from paper2saas.agents.market_skeptic import market_skeptic

idea_roaster_team = Team(
    name="IdeaRoaster",
    role="Stress-test SaaS ideas with evidence-based critique",
    model=get_mistral_model(AgentConfig.SMALL_MODEL),  # Changed from LARGE to SMALL
    # reasoning=True,
    instructions=IDEA_ROASTER_TEAM_INSTRUCTIONS,
    members=[devils_advocate, market_skeptic],
    db=shared_db,
    store_events=AgentConfig.STORE_EVENTS,
    markdown=AgentConfig.ENABLE_MARKDOWN,
    show_members_responses=AgentConfig.SHOW_MEMBER_RESPONSES,
    add_datetime_to_context=True,
)
logger.info("Initialized idea_roaster_team with 2 agents (SMALL model)")


def run_idea_roaster(idea_context: str) -> dict:
    """
    Execute idea_roaster_team with comprehensive error handling

    Args:
        idea_context: Context about the idea to critique

    Returns:
        dict with status, result/error
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Starting idea roaster critique with session ID: {session_id}")

    return run_team_with_error_handling(
        team=idea_roaster_team,
        input_text=f"Critique this SaaS idea: {idea_context}",
        log_start_msg="Starting idea roaster critique",
        log_success_msg="Successfully completed idea critique",
        session_id=session_id,
    )
