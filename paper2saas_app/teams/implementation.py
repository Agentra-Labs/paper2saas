from agno.team import Team
import uuid

from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import shared_db, logger, run_team_with_error_handling, get_mistral_model
from paper2saas_app.prompts.implementation_agents import IMPLEMENTATION_TEAM_INSTRUCTIONS

# Import agents
from paper2saas_app.agents.code_architect import code_architect
from paper2saas_app.agents.fullstack_engineer import fullstack_engineer
from paper2saas_app.agents.deployment_specialist import deployment_specialist
from paper2saas_app.agents.qa_engineer import qa_engineer

implementation_team = Team(
    name="ImplementationTeam",
    role="Build production-ready code from validated SaaS ideas",
    model=get_mistral_model(AgentConfig.LARGE_MODEL),
    stream_intermediate_steps=False,
    instructions=IMPLEMENTATION_TEAM_INSTRUCTIONS,
    members=[
        code_architect,        # LARGE_MODEL: Architecture design
        fullstack_engineer,    # LARGE_MODEL: Code generation
        deployment_specialist, # SMALL_MODEL: DevOps configs
        qa_engineer,           # SMALL_MODEL: Testing strategy
    ],
    db=shared_db,
    store_events=AgentConfig.STORE_EVENTS,
    markdown=AgentConfig.ENABLE_MARKDOWN,
    show_members_responses=AgentConfig.SHOW_MEMBER_RESPONSES,
    add_datetime_to_context=True,
    cache_session=True,
    enable_user_memories=True,
)

logger.info("Initialized implementation_team with 4 agents")


def run_implementation(idea_context: str) -> dict:
    """
    Execute implementation_team with comprehensive error handling
    
    Args:
        idea_context: Validated idea with architecture/market data
        
    Returns:
        dict with status, result/error, and metadata
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Starting implementation for session ID: {session_id}")
    
    result = run_team_with_error_handling(
        team=implementation_team,
        input_text=f"Generate production-ready implementation for: {idea_context}",
        log_start_msg="Starting implementation generation",
        log_success_msg="Successfully completed implementation",
        session_id=session_id
    )
    
    # Add session to result
    result["session_id"] = session_id
    
    # Performance metrics
    if result["status"] == "success":
        run_output = result["result"]
        metrics = {
            "total_tokens": getattr(run_output, "metrics", None) and getattr(run_output.metrics, "total_tokens", "N/A"),
            "execution_time": getattr(run_output, "metrics", None) and getattr(run_output.metrics, "time", "N/A"),
        }
        logger.info(f"Implementation Metrics: {metrics}")
        result["metrics"] = metrics
    
    return result
