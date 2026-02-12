# AGENTS.md

This file provides guidelines for agentic coding agents working in this repository.

## Project Overview

Paper2SaaS is a multi-agent AI system that transforms academic arXiv papers into SaaS business opportunities.

- **Backend**: Python 3.12+ / FastAPI / Agno multi-agent framework
- **Frontend**: Next.js 15 / TypeScript / TailwindCSS / Shadcn UI / Zustand

## Build Commands

### Frontend (agent-ui/)

```bash
cd agent-ui

# Development
bun dev                    # Start dev server on port 3000

# Build & Deploy
bun build                  # Production build
bun start                  # Start production server

# Code Quality
bun lint                   # Run ESLint
bun lint:fix               # Fix ESLint issues automatically
bun format                 # Check Prettier formatting
bun format:fix             # Fix Prettier issues
bun typecheck              # TypeScript type checking (noEmit)
bun validate               # Run lint + format + typecheck
```

### Backend (paper2saas/)

```bash
# Install dependencies
uv sync                    # Install from pyproject.toml

# Run application
uv run -m paper2saas_app.main

# Testing
cd paper2saas
pytest                     # Run all tests
pytest tests/test_file.py  # Run specific test file
pytest -v                  # Verbose output
pytest -k "test_name"      # Run tests matching pattern
```

## Code Style Guidelines

### TypeScript / Frontend

**Imports & Ordering**
- Use path aliases: `@/*` maps to `./src/*`
- Group imports: React → external libs → internal components → utilities
- Use absolute imports within src directory

**Formatting (Prettier)**
```javascript
// prettier.config.cjs
singleQuote: true
semi: false
trailingComma: 'none'
```

**TypeScript**
- Strict mode enabled in `tsconfig.json`
- Use explicit types for function parameters and return types
- Avoid `any`; use `unknown` or proper type definitions
- Use interface for object types, type for unions/primitives

**Naming Conventions**
- Components: PascalCase (e.g., `AgentChat.tsx`)
- Hooks: camelCase with `use` prefix (e.g., `useStore.ts`)
- Files: kebab-case for non-components, PascalCase for components
- Constants: SCREAMING_SNAKE_CASE

**Styling (TailwindCSS)**
- Use Shadcn UI component patterns
- Use `cn()` utility (clsx + tailwind-merge) for conditional classes
- Custom colors defined in `tailwind.config.ts`: `primary`, `brand`, `background`, `secondary`, `accent`, `muted`, `destructive`, `positive`
- Use CSS variables for dark mode support

**Component Patterns**
- Use `class-variance-authority` (cva) for component variants
- Wrap with Radix UI primitives for accessible components
- Use `framer-motion` for animations

**State Management (Zustand)**
- Store definition in `src/store.ts`
- Use persist middleware for persistent state

### Python / Backend

**Models & Types**
- Use Pydantic models for all structured data
- Define models in `paper2saas_app/models.py`
- Use Agno's `Agent` and `Team` classes for agents

**Agents**
- Define individual agents in `paper2saas_app/agents/`
- Use structured outputs (Pydantic schemas) to prevent hallucination
- Include reasoning steps via `reasoning` parameter
- Follow fallback chain: ArxivTools → FirecrawlTools → WebsiteTools → BaiduSearchTools

**Error Handling**
- Log errors to `tmp/paper2saas.log`
- Use structured error responses for API endpoints
- Wrap UI components in Error Boundaries for stability

## Directory Structure

```
paper2saas/
├── agent-ui/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # Reusable UI components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utility functions
│   │   └── store.ts      # Zustand store
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── paper2saas/            # Python backend
│   ├── paper2saas_app/   # Main application package
│   │   ├── agents/       # Agent definitions
│   │   ├── teams/        # Team orchestration
│   │   ├── prompts/      # Agent instructions
│   │   ├── models.py     # Pydantic models
│   │   └── config.py     # Settings
│   └── tests/            # Pytest fixtures
└── pyproject.toml        # Python dependencies
```

## Key Configuration

**Environment Variables**
- `MISTRAL_API_KEY` - Required for LLM calls
- `FIRECRAWL_API_KEY` - Required for web scraping
- `LARGE_MODEL` - Default: `mistral:mistral-large-latest`
- `SMALL_MODEL` - Default: `mistral:mistral-small-latest`
- `LOG_LEVEL` - Default: INFO

**Frontend Environment**
- Use localStorage for persistence (see `NODE_OPTIONS='--localstorage-file=.localstorage'` in dev)
- Configure API base URL in frontend API routes

## Adding New Features

1. **New Agent**:
   - Define Pydantic output schema in `models.py`
   - Add instructions to `prompts/agents.py`
   - Create agent in `agents/`
   - Register in `teams/`

2. **New UI Component**:
   - Follow Shadcn UI patterns
   - Use Radix UI primitive if available
   - Add CVA variants for styling
   - Export from `components/` with barrel export

3. **New API Endpoint**:
   - Add to FastAPI app in backend
   - Create corresponding API route in `agent-ui/src/api/`
   - Update store if state needed

## Testing Strategy

- **Backend**: Use pytest fixtures from `tests/conftest.py`
- **Frontend**: Manual testing via dev server
- **Integration**: Test API endpoints with `curl` or Postman
- **Database**: SQLite at `tmp/paper2saas.db` for event persistence
