"""Team orchestration for multi-agent workflows

Teams available:
- paper2saas_team: 8-agent pipeline for paper → SaaS transformation
- idea_roaster_team: 2-agent critique team for stress-testing ideas
"""

from .paper2saas import paper2saas_team, run_paper2saas, arun_paper2saas
from .roaster import idea_roaster_team

__all__ = [
    "paper2saas_team",
    "run_paper2saas",
    "arun_paper2saas",
    "idea_roaster_team",
]
