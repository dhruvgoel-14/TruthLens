
import asyncio
import inspect
from typing import Any

from tinyfish import TinyFish

from app.config import TINYFISH_API_KEY


def _to_dict(result: Any) -> Any:
    """Convert SDK response objects into JSON-compatible data."""

    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")

    if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
        return result

    return str(result)


async def search_one(query: str) -> dict[str, Any]:
    """Run one TinyFish search query and return its results."""

    query = query.strip() if isinstance(query, str) else ""

    if not query:
        raise ValueError("Search query cannot be empty.")

    client = TinyFish(api_key=TINYFISH_API_KEY)

    try:
        result = client.search.query(query=query)

        if inspect.isawaitable(result):
            result = await result

        return {
            "query": query,
            "results": _to_dict(result),
            "error": None,
        }

    except Exception as exc:
        # Preserve the error so one failed query need not stop all searches.
        return {
            "query": query,
            "results": [],
            "error": f"{type(exc).__name__}: {exc}",
        }

    finally:
        close = getattr(client, "close", None)

        if close:
            result = close()

            if inspect.isawaitable(result):
                await result


async def search_many(
    queries: list[str],
    max_queries: int = 5,
) -> dict[str, Any]:
    """Search several queries and retain each query's outcome."""

    if not isinstance(queries, list):
        raise TypeError("queries must be a list of strings.")

    if not 1 <= max_queries <= 10:
        raise ValueError("max_queries must be between 1 and 10.")

    cleaned_queries = []
    seen = set()

    for query in queries:
        if not isinstance(query, str):
            continue

        query = query.strip()

        if query and query.casefold() not in seen:
            cleaned_queries.append(query)
            seen.add(query.casefold())

    cleaned_queries = cleaned_queries[:max_queries]

    if not cleaned_queries:
        raise ValueError("At least one non-empty search query is required.")

    # Keep requests sequential initially to avoid unnecessary API load.
    outcomes = []

    for query in cleaned_queries:
        outcomes.append(await search_one(query))

    successful = sum(item["error"] is None for item in outcomes)

    return {
        "queries_attempted": len(cleaned_queries),
        "queries_succeeded": successful,
        "queries_failed": len(cleaned_queries) - successful,
        "searches": outcomes,
    }
