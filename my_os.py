from agno.os import AgentOS
from paper2saas import (
    paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    report_generator,
    paper2saas_workflow,
    workflow_agent,
)

paper2saas_os = AgentOS(
    name="paper2saas-os",
    description="Transforms academic papers into validated SaaS opportunities",
    agents=[
        workflow_agent,  # Main entrypoint
        paper_analyzer,
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
    ],
    workflows=[paper2saas_workflow],
)

app = paper2saas_os.get_app()

if __name__ == "__main__":
    paper2saas_os.serve(app="my_os:app", reload=True)  # Adjust module name if needed