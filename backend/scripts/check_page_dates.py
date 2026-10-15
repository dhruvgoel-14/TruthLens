
import asyncio

from app.pipeline.fetcher import fetch_urls


async def main():
    urls = [
        "https://www.pib.gov.in/Allrel.aspx?reg=3&lang=1",
        "https://www.pib.gov.in/Content/224_5_AboutPIB.aspx",
        "https://mib.gov.in/en/ministry/organizations/press-information-bureau-government-india",
    ]

    print("Fetching known URLs directly through TinyFish...")

    fetched = await fetch_urls(urls)

    response = fetched.get("response") or {}
    pages = response.get("results", [])

    print(f"\nPages fetched: {len(pages)}")
    print("Fetcher error:", fetched.get("error"))

    if not pages:
        print("No pages fetched. Check the fetcher's error details:")
        print(repr(response)[:3000])
        return

    for index, page in enumerate(pages, start=1):
        print(f"\n{'=' * 55}")
        print(f"PAGE {index}")
        print("=" * 55)

        print("Available fields:", list(page.keys()))

        print("\nPossible date fields:")

        found = False
        for key, value in page.items():
            if any(
                word in key.lower()
                for word in ("date", "time", "publish", "modified")
            ):
                print(f"{key}: {value!r}")
                found = True

        if not found:
            print("No obvious date fields in the returned metadata.")

        print("\npublished_date:", repr(page.get("published_date")))

        # Display a small text sample to help identify visible dates.
        text = page.get("text", "")
        print("\nPage text sample:")
        print(text[:700] if isinstance(text, str) else repr(text))


if __name__ == "__main__":
    asyncio.run(main())
