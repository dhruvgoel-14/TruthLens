
from typing import Any

from app.pipeline.planner import generate_queries
from app.pipeline.search import search_many


async def research_claim(claim: str) -> dict[str, Any]:
    """
    Generate search queries for a claim and search for relevant sources.
    """

    # Stage 1: Ask Gemini to generate focused search queries.
    plan = generate_queries(claim)

    # Stage 2: Search those queries using TinyFish.
    search_results = await search_many(
        plan["search_queries"],
        max_queries=5,
    )

    return {
        "claim": plan["claim"],
        "search_queries": plan["search_queries"],
        "search_results": search_results,
    }
