from agno.os import AgentOS

from paper2saas import (
    workflow_agent,
    paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    report_generator,
    paper2saas_workflow,
)

paper2saas_os = AgentOS(
    name="paper2saas-os",
    description="Transforms academic papers into validated SaaS opportunities",
    agents=[
        workflow_agent,  # ← Main chat interface
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
    paper2saas_os.serve(app="__main__:app", reload=True)