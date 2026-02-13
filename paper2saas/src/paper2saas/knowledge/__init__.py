"""
Shared Knowledge Base for Research-to-SaaS Platform

Uses LanceDb (lightweight, local vector store) with MistralEmbedder
to store and retrieve academic paper content.
"""

import logging
from pathlib import Path

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.mistral import MistralEmbedder
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb, SearchType

logger = logging.getLogger(__name__)

# Setup paths
KNOWLEDGE_DIR = Path("tmp/lancedb")
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


# Create the shared knowledge base
research_knowledge = Knowledge(
    vector_db=LanceDb(
        table_name="research_papers",
        uri=str(KNOWLEDGE_DIR),
        search_type=SearchType.vector,
        embedder=MistralEmbedder(id="mistral-embed"),
    ),
)


def add_arxiv_paper(arxiv_id: str) -> bool:
    """Add an arXiv paper to the knowledge base.

    Args:
        arxiv_id: arXiv paper ID (e.g., "2301.12345") or full URL

    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract just the ID if full URL provided
        if "arxiv.org" in arxiv_id:
            arxiv_id = arxiv_id.split("/")[-1].replace(".pdf", "")

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        research_knowledge.insert(
            url=pdf_url,
            reader=PDFReader(),
        )
        return True
    except (OSError, ValueError) as e:
        logger.error("Failed to add paper %s: %s", arxiv_id, e)
        return False


def add_pdf_url(url: str) -> bool:
    """Add a PDF from URL to the knowledge base.

    Args:
        url: Direct URL to a PDF file

    Returns:
        True if successful, False otherwise
    """
    try:
        research_knowledge.insert(
            url=url,
            reader=PDFReader(),
        )
        return True
    except (OSError, ValueError) as e:
        logger.error("Failed to add PDF %s: %s", url, e)
        return False


def search_papers(query: str, limit: int = 5) -> list:
    """Search the knowledge base for relevant paper content.

    Args:
        query: Natural language search query
        limit: Maximum number of results (note: Knowledge.search uses max_results parameter)

    Returns:
        List of relevant document chunks
    """
    try:
        # Knowledge.search() doesn't accept 'limit', it uses the max_results from initialization
        results = research_knowledge.search(query=query)
        return results
    except (OSError, ValueError) as e:
        logger.error("Failed to search papers for '%s': %s", query, e)
        return []


__all__ = [
    "research_knowledge",
    "add_arxiv_paper",
    "add_pdf_url",
    "search_papers",
]
