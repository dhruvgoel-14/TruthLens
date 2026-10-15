
import asyncio
import json

from app.pipeline.research import research_claim


async def main():
    claim = (
        "The government announced a nationwide school closure "
        "starting tomorrow."
    )

    print("Running TruthLens research pipeline...\n")

    result = await research_claim(claim)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    print("\nResearch stage completed.")
    print("Queries generated:", len(result["search_queries"]))
    print(
        "Successful searches:",
        result["search_results"]["queries_succeeded"],
    )
    print(
        "Failed searches:",
        result["search_results"]["queries_failed"],
    )


if __name__ == "__main__":
    asyncio.run(main())
