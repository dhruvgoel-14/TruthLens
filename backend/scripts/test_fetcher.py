
import asyncio
import json

from app.pipeline.fetcher import fetch_urls


async def main():
    urls = [
        "https://www.india.gov.in/",
        "https://www.pib.gov.in/",
    ]

    print("Testing TruthLens webpage fetcher...\n")

    result = await fetch_urls(urls)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    if result["error"]:
        print("\nFetch request failed:", result["error"])
    else:
        print("\nFetch request completed. Inspect the response for page content and errors.")


if __name__ == "__main__":
    asyncio.run(main())
