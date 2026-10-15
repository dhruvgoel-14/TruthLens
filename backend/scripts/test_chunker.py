
import asyncio
import json

from app.pipeline.fetcher import fetch_urls
from app.pipeline.chunker import chunk_pages


async def main():
    urls = [
        "https://www.india.gov.in/",
        "https://www.pib.gov.in/",
    ]

    print("Fetching pages for the chunker test...\n")

    fetched = await fetch_urls(urls)

    if fetched["error"]:
        print("Fetch failed:", fetched["error"])
        return

    chunks = chunk_pages(
        fetched,
        chunk_size=100,
        overlap=15,
    )

    print("Total evidence chunks:", len(chunks))
    print("\nFirst three chunks:\n")

    print(
        json.dumps(
            chunks[:3],
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
