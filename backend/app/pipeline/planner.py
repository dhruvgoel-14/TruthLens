
import re
from typing import Any

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODEL


PLANNER_PROMPT = """
You are the search planner for TruthLens, a claim-verification system.

Your job is to create search queries that help investigate a claim.
You must not decide whether the claim is true or false.

Rules:
1. Generate 4 to 6 distinct, useful search queries.
2. Include the main entities, event, or subject of the claim.
3. Search for primary sources, official statements, and reliable reporting.
4. Include a query that searches for evidence contradicting the claim.
5. Preserve important dates, locations, numbers, and names.
6. Do not invent facts or assume the claim is true.
7. Use the claim's language when appropriate.
8. Return only the requested structured output.
"""


class PlannerOutput(dict):
    """Dictionary-compatible planner result."""


def _clean_claim(claim: str) -> str:
    """Validate and normalize a user-provided claim."""

    if not isinstance(claim, str):
        raise TypeError("Claim must be a string.")

    claim = re.sub(r"\s+", " ", claim).strip()

    if not claim:
        raise ValueError("Claim cannot be empty.")

    if len(claim) > 2000:
        raise ValueError("Claim must be 2000 characters or fewer.")

    return claim


def generate_queries(claim: str) -> dict[str, Any]:
    """
    Generate search queries for a claim using Gemini.

    Returns:
        {
            "claim": "...",
            "search_queries": ["...", "..."]
        }
    """

    claim = _clean_claim(claim)

    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=(
                f"{PLANNER_PROMPT}\n\n"
                f"Claim to investigate:\n{claim}"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "search_queries": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                        }
                    },
                    "required": ["search_queries"],
                },
                temperature=0.2,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty planner response.")

        import json

        data = json.loads(response.text)
        queries = data.get("search_queries", [])

        if not isinstance(queries, list):
            raise ValueError("Planner output must contain a list of queries.")

        cleaned_queries = []
        seen = set()

        for query in queries:
            if not isinstance(query, str):
                continue

            query = re.sub(r"\s+", " ", query).strip()

            if query and query.casefold() not in seen:
                cleaned_queries.append(query)
                seen.add(query.casefold())

        if not cleaned_queries:
            raise ValueError("Planner did not generate any usable queries.")

        return {
            "claim": claim,
            "search_queries": cleaned_queries[:6],
        }

    finally:
        client.close()
