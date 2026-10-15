
import asyncio
import json

from app.pipeline.search import search_many


async def main():
    queries = [
        "official government news India",
        "India government official announcements",
    ]

    print("Testing TruthLens search module...\n")

    result = await search_many(queries, max_queries=5)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    if result["queries_succeeded"] == 0:
        print("\nNo searches succeeded. Check the error messages above.")
    else:
        print("\nAt least one search succeeded!")


if __name__ == "__main__":
    asyncio.run(main())
