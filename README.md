# Paper2SaaS

Multi-agent AI system that transforms academic arXiv papers into validated SaaS business opportunities.

## Overview

Paper2SaaS uses a team of specialized AI agents to:
1. Analyze academic papers from arXiv
2. Research market opportunities and pain points
3. Generate SaaS ideas based on paper innovations
4. Validate ideas with market research
5. Provide strategic recommendations
6. Create technical implementation plans (GitHub repos, architecture, MVP timeline)
7. Produce comprehensive opportunity reports

## Tech Stack

- **Python**: 3.12+
- **Framework**: [Agno](https://github.com/agnohq/agno) - Multi-agent orchestration
- **LLM**: Mistral AI (mistral-large, mistral-small)
- **API**: FastAPI
- **Database**: SQLite (agent event persistence)
- **Tools**: ArxivTools, FirecrawlTools, WebsiteTools, BaiduSearchTools, HackerNewsTools

### Frontend (Agent UI)
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: TailwindCSS, Shadcn UI
- **State Management**: Zustand
- **Runtime**: Bun (or Node/pnpm)

## Architecture

### Main Team: paper2saas_team (8 agents)

Sequential workflow with parallel execution phases:
1. **PaperAnalyzer** - Fetches and analyzes arXiv papers with fallback protocol
2. **MarketResearcher** - Conducts tool-based market research
3. **IdeaGenerator** - Creates SaaS ideas from verified inputs
4. **ValidationResearcher** (Parallel) - Validates top ideas with external research
5. **ProductEngineer** (Parallel) - Finds GitHub repos and creates technical implementation plans
6. **StrategicAdvisor** - Evaluates and scores ideas based on validation and technical feasibility
7. **FactChecker** - Verifies claims against sources
8. **ReportGenerator** - Compiles comprehensive final report

### Critique Team: idea_roaster_team (2 agents)

Parallel critique for stress-testing:
- **DevilsAdvocate** - Technical critique with tool-verified evidence
- **MarketSkeptic** - Market assumptions challenge

### Implementation Team: implementation_team (4 agents)

Builds production-ready code from validated ideas:
- **CodeArchitect** - Designs system architecture and tech stack
- **FullStackEngineer** - Generates production code (backend + frontend)
- **DeploymentSpecialist** - Creates Docker, K8s, and CI/CD configurations
- **QAEngineer** - Designs testing strategy and QA plans

### Frontend: Agent UI
A modern, reactive web interface built with Next.js that provides:
- Real-time streaming of agent activities
- Artifact rendering (Reports, Code, Markdown)
- Theme support (Light/Dark/System)
- Session management
- **Robust Error Handling**: UI components wrapped in Error Boundaries for stability

## Key Features

- **Structured Outputs**: Pydantic models prevent hallucination
- **Chain-of-Note (CoN)**: Systematic source tracking
- **Chain-of-Verification (CoVe)**: Claim verification protocol
- **Multi-Tool Fallback**: ArxivTools → FirecrawlTools → WebsiteTools → BaiduSearchTools
- **Reasoning**: All agents have configurable reasoning steps
- **Event Persistence**: SQLite storage for debugging and analysis
- **Rich Agent UI**: Interactive chat interface with Claude-style [Artifacts support](ARTIFACTS_GUIDE.md)

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager (Backend)
- [Bun](https://bun.sh) runtime (Frontend)

### Installation

```bash
# Clone repo
git clone <repo-url>
cd paper2saas

# Install Backend dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys (MISTRAL_API_KEY, FIRECRAWL_API_KEY)

# Install Frontend dependencies
cd agent-ui
bun install
# or if using pnpm
# pnpm install
cd ..
```

### Environment Variables

Required:
- `MISTRAL_API_KEY` - Your Mistral AI API key
- `FIRECRAWL_API_KEY` - Your Firecrawl API key

Optional (Model Overrides):
- `LARGE_MODEL` - Default: mistral:mistral-large-latest
- `SMALL_MODEL` - Default: mistral:mistral-small-latest
- `PRODUCT_ENGINEER_MODEL` - Specific override for Product Engineer
- `VALIDATION_RESEARCHER_MODEL` - Specific override for Validation Researcher
- ... (see `paper2saas_app/config.py` for full list)

Configuration:
- `REASONING_MIN_STEPS` - Default: 2
- `REASONING_MAX_STEPS` - Default: 8
- `ENABLE_MARKDOWN` - Default: true
- `STORE_EVENTS` - Default: true
- `SHOW_MEMBER_RESPONSES` - Default: true
- `LOG_LEVEL` - Default: INFO

## Usage

### 1. Start the Backend (API)

```bash
# Start the backend server
uv run -m paper2saas_app.main
```

### 2. Start the Frontend (UI)

```bash
cd agent-ui
bun dev
```

- Backend API: `http://localhost:8000` (or `http://localhost:7777` depending on Agno config)
- Frontend UI: `http://localhost:3000`

### API Endpoints

- `GET /` - Health check
- `POST /paper2saas/run` - Analyze paper and generate opportunities
  ```json
  {
    "arxiv_id": "2512.24991v1"
  }
  ```

### Example Usage

```python
import requests

response = requests.post(
    "http://localhost:8000/paper2saas/run",
    json={"arxiv_id": "2512.24991v1"}
)

print(response.json())
```

## Project Structure

```
paper2saas/
├── paper2saas_app/        # Modular Application Package
│   ├── agents/            # Individual Agent Definitions
│   ├── teams/             # Team Orchestration Logic
│   ├── prompts/           # Agent Instructions & Prompts
│   ├── config.py          # Configuration & Settings
│   ├── models.py          # Pydantic Data Models
│   └── utils.py           # Shared Utilities
├── paper2saas.py          # Legacy Facade (Backward Compatibility)
├── my_os.py               # AgentOS setup and FastAPI app
├── pyproject.toml         # Python Dependencies
├── .env                   # Environment variables (not in git)
├── tmp/
│   ├── paper2saas.db      # SQLite event storage
│   └── paper2saas.log     # Application logs
├── agent-ui/              # Next.js Frontend application
├── ARTIFACTS_GUIDE.md     # Documentation for UI Artifacts
└── README.md
```

## Development

### Logging

Logs are written to:
- Console (stdout)
- `tmp/paper2saas.log`

Configure log level with `LOG_LEVEL` environment variable.

### Database

Agent events are stored in `tmp/paper2saas.db` for:
- Debugging agent interactions
- Analyzing workflow performance
- Context sharing between agents

### Adding New Agents

1. Define Pydantic output schema in `paper2saas_app/models.py`
2. Add instructions to `paper2saas_app/prompts/agents.py`
3. Create Agent definition in `paper2saas_app/agents/`
4. Register agent in `paper2saas_app/teams/paper2saas.py`
5. Update `AgentConfig` in `paper2saas_app/config.py` if new model settings are needed

## Methodology

### Anti-Hallucination Measures

1. **Structured Outputs**: All agents use Pydantic schemas
2. **Source Attribution**: Every claim must cite tool/source
3. **Chain-of-Note**: Systematic reading notes before synthesis
4. **Chain-of-Verification**: Post-draft claim verification
5. **Fact Checking**: Dedicated agent verifies claims
6. **Data Quality Metrics**: Confidence scores, tool success rates

### Tool Usage Protocol

- Primary tool attempts first
- Automatic fallback chain on failure
- All attempts logged
- Confidence scoring based on source quality

## Troubleshooting

### Common Issues

**Error: Missing API keys**
- Ensure `.env` file exists with valid keys
- Check `MISTRAL_API_KEY` and `FIRECRAWL_API_KEY`

**Error: Database locked**
- Only one process can write to SQLite at a time
- Restart the server

**Low confidence scores**
- Verify arXiv ID is correct
- Check if paper is accessible
- Review logs in `tmp/paper2saas.log`

**UI Rendering Error**
- If a message displays "Rendering Error", the content likely contained malformed markdown.
- Check the console for details. The app will remain stable thanks to Error Boundaries.

## Contributing

Currently in active development. Main contributor: ash_blanc

## License

[Add license information]