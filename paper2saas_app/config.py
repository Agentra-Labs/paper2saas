import os
from dotenv import load_dotenv

load_dotenv()

# Environment setup
os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY", "")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

class AgentConfig:
    """Centralized configuration for all agents"""
    # Models
    LARGE_MODEL = os.getenv("LARGE_MODEL", "mistral:mistral-large-latest")
    SMALL_MODEL = os.getenv("SMALL_MODEL", "mistral:mistral-small-latest")
    
    # Specific Agent Models
    MARKET_RESEARCHER_MODEL = os.getenv("MARKET_RESEARCHER_MODEL", SMALL_MODEL)
    VALIDATION_RESEARCHER_MODEL = os.getenv("VALIDATION_RESEARCHER_MODEL", LARGE_MODEL)
    STRATEGIC_ADVISOR_MODEL = os.getenv("STRATEGIC_ADVISOR_MODEL", LARGE_MODEL)
    FACT_CHECKER_MODEL = os.getenv("FACT_CHECKER_MODEL", SMALL_MODEL)
    DEVILS_ADVOCATE_MODEL = os.getenv("DEVILS_ADVOCATE_MODEL", LARGE_MODEL)
    MARKET_SKEPTIC_MODEL = os.getenv("MARKET_SKEPTIC_MODEL", LARGE_MODEL)
    
    # Reasoning settings
    REASONING_MIN_STEPS = int(os.getenv("REASONING_MIN_STEPS", "2"))
    REASONING_MAX_STEPS = int(os.getenv("REASONING_MAX_STEPS", "8"))
    
    # Feature flags
    ENABLE_MARKDOWN = os.getenv("ENABLE_MARKDOWN", "true").lower() == "true"
    STORE_EVENTS = os.getenv("STORE_EVENTS", "true").lower() == "true"
    SHOW_MEMBER_RESPONSES = os.getenv("SHOW_MEMBER_RESPONSES", "true").lower() == "true"
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Implementation Team Models
    ARCHITECT_MODEL = os.getenv("ARCHITECT_MODEL", LARGE_MODEL)
    ENGINEER_MODEL = os.getenv("ENGINEER_MODEL", LARGE_MODEL)
    DEPLOYMENT_MODEL = os.getenv("DEPLOYMENT_MODEL", SMALL_MODEL)
    QA_MODEL = os.getenv("QA_MODEL", SMALL_MODEL)
