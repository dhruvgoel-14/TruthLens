
import asyncio
from typing import Any

from app.pipeline.planner import generate_queries
from app.pipeline.progress import ProgressCallback, emit
from app.pipeline.search import search_many


async def research_claim(
    claim: str,
    on_progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    """
    Generate search queries for a claim and search for relevant sources.
    """

    # Stage 1: Ask Gemini to generate focused search queries.
    # The Gemini SDK call is blocking, so run it in a worker thread to keep
    # the event loop (and progress streaming) responsive.
    await emit(on_progress, "planning")
    plan = await asyncio.to_thread(generate_queries, claim)
    await emit(on_progress, "planned", queries=plan["search_queries"])

    # Stage 2: Search those queries using TinyFish.
    search_results = await search_many(
        plan["search_queries"],
        max_queries=5,
        on_progress=on_progress,
    )

    return {
        "claim": plan["claim"],
        "search_queries": plan["search_queries"],
        "search_results": search_results,
    }
