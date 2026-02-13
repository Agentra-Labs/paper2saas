# Knowledge Base Sharing Architecture

## Overview

The Paper2SaaS system uses a **shared knowledge base** that enables cross-session knowledge access between agents. This means papers analyzed by the Paper Analyzer in one session can be accessed by the Market Researcher in a completely different session.

## Architecture

### Shared Knowledge Base

```python
# Location: paper2saas/src/paper2saas/knowledge/__init__.py

research_knowledge = Knowledge(
    vector_db=LanceDb(
        table_name="research_papers",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=MistralEmbedder(id="mistral-embed"),
    ),
)
```

### Key Components

1. **Vector Database**: LanceDb (lightweight, local, disk-persisted)
2. **Storage Location**: `tmp/lancedb/research_papers.lance`
3. **Embedder**: MistralEmbedder for semantic search
4. **Search Type**: Vector search for semantic similarity

### Agents with Knowledge Access

The following agents have access to the shared knowledge base:

1. **Paper Discovery Agent** (`discovery.py`)
   - Has `knowledge=research_knowledge`
   - Has `search_knowledge=True`
   - Can add papers and search the KB

2. **Paper Analyzer** (`paper_analyzer.py`)
   - Has `knowledge=research_knowledge`
   - Has `search_knowledge=True`
   - Can analyze papers and access previously indexed papers

3. **Market Researcher** (`market_researcher.py`)
   - Has `knowledge=research_knowledge`
   - Has `search_knowledge=True`
   - Can access papers analyzed by other agents

## Cross-Session Knowledge Sharing

### How It Works

```
Session A (Paper Analyzer)
    ↓
Analyzes arXiv paper 2602.04503
    ↓
Paper content stored in LanceDb
    ↓
Persisted to disk: tmp/lancedb/research_papers.lance
    ↓
Session B (Market Researcher)
    ↓
Searches for "multimodal learning"
    ↓
Retrieves content from paper 2602.04503
    ↓
✓ Cross-session access successful!
```

### Key Points

- **Session IDs** isolate conversation history (stored in SQLite)
- **Knowledge Base** is shared across ALL sessions (stored in LanceDb)
- **Persistence**: LanceDb writes vectors to disk, so knowledge survives restarts
- **Automatic RAG**: With `search_knowledge=True`, agents automatically search KB when relevant

## Usage Examples

### Adding Papers to Knowledge Base

```python
from paper2saas.knowledge import add_arxiv_paper

# Add a paper (can be done by any agent with knowledge access)
add_arxiv_paper("2602.04503")
```

### Searching Knowledge Base

```python
from paper2saas.knowledge import search_papers

# Search for relevant content
results = search_papers("multimodal transformers")
```

### Agent Usage

```python
# Session A: Paper Analyzer analyzes a paper
paper_analyzer.run(
    "Analyze arXiv paper 2602.04503",
    session_id="session-a"
)

# Session B: Market Researcher can access that paper's content
market_researcher.run(
    "What are the market opportunities for multimodal learning?",
    session_id="session-b"  # Different session!
)
# Market Researcher will automatically search the KB and find paper 2602.04503
```

## Database Architecture

### Two Separate Databases

1. **Session Database** (SQLite)
   - Location: `tmp/paper2saas.db` (team agents) or `tmp/paper2saas_agents.db` (discovery agents)
   - Stores: Conversation history, agent runs, session metadata
   - Scope: Per-session isolation

2. **Knowledge Database** (LanceDb)
   - Location: `tmp/lancedb/research_papers.lance`
   - Stores: Paper content vectors, embeddings
   - Scope: Global, shared across all sessions

### Why Two Databases?

- **Session DB**: Keeps conversations separate (privacy, context management)
- **Knowledge DB**: Enables knowledge reuse across sessions (efficiency, consistency)

## Benefits

1. **Efficiency**: Papers are indexed once, used many times
2. **Consistency**: All agents work from the same knowledge base
3. **Context Preservation**: Each session maintains its own conversation history
4. **Scalability**: LanceDb is lightweight and fast for local deployments

## Testing

Run the knowledge sharing test:

```bash
cd paper2saas
uv run python test_knowledge_sharing.py
```

This verifies:
- Knowledge base storage location
- Agent knowledge access
- Cross-session knowledge persistence

## Verification

To verify agents share the same knowledge instance:

```python
from paper2saas.agents.paper_analyzer import paper_analyzer
from paper2saas.agents.market_researcher import market_researcher

# Check they have the same LanceDb instance
print(id(paper_analyzer.knowledge.vector_db))
print(id(market_researcher.knowledge.vector_db))
# Should print the same memory address
```

## Future Enhancements

Potential improvements to the knowledge sharing system:

1. **Metadata Tagging**: Add tags to papers for better filtering
2. **Hybrid Search**: Combine vector + keyword search for better retrieval
3. **Knowledge Expiry**: Implement TTL for outdated papers
4. **Multi-Tenancy**: Separate knowledge bases per user/organization
5. **Cloud Storage**: Move from local LanceDb to cloud vector DB (Pinecone, Weaviate)

## Troubleshooting

### Knowledge Not Found

If agents can't find previously indexed papers:

1. Check if LanceDb directory exists: `ls -la tmp/lancedb/`
2. Verify embedder API key is set (Mistral API key)
3. Check if paper was successfully indexed (no errors during insert)

### Embedding Errors

If you see "401 Unauthorized" errors:

```bash
# Set Mistral API key
export MISTRAL_API_KEY="your-key-here"
```

### Performance Issues

If searches are slow:

1. Consider switching to hybrid search (vector + keyword)
2. Reduce `max_results` in Knowledge configuration
3. Use more specific search queries

## Related Files

- `paper2saas/src/paper2saas/knowledge/__init__.py` - Knowledge base setup
- `paper2saas/src/paper2saas/agents/paper_analyzer.py` - Paper Analyzer with KB
- `paper2saas/src/paper2saas/agents/market_researcher.py` - Market Researcher with KB
- `paper2saas/src/paper2saas/agents/discovery.py` - Discovery Agent with KB
- `paper2saas/test_knowledge_sharing.py` - Knowledge sharing tests
