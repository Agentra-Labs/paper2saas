import os
import logging
import warnings
from dotenv import load_dotenv

load_dotenv()

from agno.models.mistral import MistralChat

# Suppress annoying OpenAI API key warnings
# These occur because Agno might auto-initialize OpenAI client even when using Mistral
warnings.filterwarnings("ignore", message="The api_key client option must be set")

# Configure logging (only if enabled)
if os.getenv("ENABLE_LOGGING", "true").lower() == "true":
    log_handlers = [logging.StreamHandler()]
    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        log_handlers.append(logging.FileHandler("tmp/paper2saas.log"))

    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=log_handlers,
    )
    logger = logging.getLogger(__name__)
else:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# --- Database for session storage ---
# Try Supabase first, fallback to SQLite
SUPABASE_PROJECT = os.getenv("SUPABASE_PROJECT")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

os.makedirs("tmp", exist_ok=True)

if SUPABASE_PROJECT and SUPABASE_PASSWORD:
    try:
        from agno.db.postgres import PostgresDb

        SUPABASE_DB_URL = f"postgresql://postgres.{SUPABASE_PROJECT}:{SUPABASE_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        shared_db = PostgresDb(db_url=SUPABASE_DB_URL)
        # Attempt a simple operation if possible, or just trust the init for now
        # Agno's PostgresDb usually validates on first use, but we want to catch OperationalError here if it happens during init
        logger.info("Using Supabase PostgreSQL for session storage")
    except Exception as e:
        from agno.db.sqlite import SqliteDb

        logger.warning(f"Failed to connect to Supabase: {e}. Falling back to SQLite.")
        shared_db = SqliteDb(db_file="tmp/paper2saas.db")
else:
    # Fallback to SQLite if Supabase credentials not configured
    from agno.db.sqlite import SqliteDb

    shared_db = SqliteDb(db_file="tmp/paper2saas.db")
    logger.info("Using SQLite for session storage (set SUPABASE_PROJECT/PASSWORD for PostgreSQL)")


import itertools
from typing import Iterator

# ... (existing imports)

# Initialize key rotation
_mistral_keys = [k.strip() for k in os.getenv("MISTRAL_API_KEY", "").split(",") if k.strip()]
_key_cycle: Iterator[str] | None = itertools.cycle(_mistral_keys) if _mistral_keys else None

if not _mistral_keys:
    logger.warning("No MISTRAL_API_KEY found in environment variables!")

def get_mistral_model(model_id: str) -> MistralChat:
    """Returns a MistralChat model instance with the given ID, rotating keys."""
    # Strip provider prefix if present
    clean_id = model_id.split(":")[-1] if ":" in model_id else model_id
    
    # Get next key from cycle
    api_key = next(_key_cycle) if _key_cycle else None
    
    return MistralChat(id=clean_id, api_key=api_key)


def validate_arxiv_id(arxiv_id: str) -> bool:
    """Validate arXiv ID format"""
    import re

    pattern = r"^\d{4}\.\d{4,5}(v\d+)?$"
    return bool(re.match(pattern, arxiv_id))


def run_team_with_error_handling(
    team, input_text: str, log_start_msg: str, log_success_msg: str, session_id: str | None = None
) -> dict:
    """
    Generic wrapper for executing a team with error handling.

    Args:
        team: The team instance to run
        input_text: The input prompt for the team
        log_start_msg: Message to log at start
        log_success_msg: Message to log on success
        session_id: Optional session ID to ensure isolation

    Returns:
        dict with status, result/error
    """
    logger.info(log_start_msg)

    try:
        # Pass session_id if provided
        kwargs = {"session_id": session_id} if session_id else {}
        result = team.run(input_text, **kwargs)
        logger.info(log_success_msg)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Error during execution: %s", e, exc_info=True)
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


async def arun_team_with_error_handling(
    team, input_text: str, log_start_msg: str, log_success_msg: str, session_id: str | None = None
) -> dict:
    """
    Async wrapper for executing a team with error handling.
    Uses team.arun() for concurrent member execution.

    Args:
        team: The team instance to run
        input_text: The input prompt for the team
        log_start_msg: Message to log at start
        log_success_msg: Message to log on success
        session_id: Optional session ID to ensure isolation

    Returns:
        dict with status, result/error
    """
    logger.info(log_start_msg)

    try:
        # Pass session_id if provided
        kwargs = {"session_id": session_id} if session_id else {}
        result = await team.arun(input_text, **kwargs)
        logger.info(log_success_msg)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Error during execution: %s", e, exc_info=True)
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}
