
import asyncio
import inspect
import json
from pathlib import Path

from tinyfish import TinyFish
from app.config import TINYFISH_API_KEY

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "tests" / "fixtures"

# Use a URL returned by your successful Search smoke test.
TEST_URL = "https://www.india.gov.in/news/news-on-air"


def to_jsonable(result):
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    if isinstance(result, (dict, list, str, int, float, bool, type(None))):
        return result
    return str(result)


async def main():
    print("TinyFish Fetch smoke test")
    client = TinyFish(api_key=TINYFISH_API_KEY)

    try:
        fetch = getattr(client, "fetch", None)

        if fetch is None:
            print("No 'fetch' attribute found on the client.")
            print([name for name in dir(client) if not name.startswith("_")])
            return

        print("Fetch methods:")
        print([name for name in dir(fetch) if not name.startswith("_")])

        method = getattr(fetch, "get_contents", None)

        if method is None:
            print("fetch.get_contents was not found.")
            return

        print("Method signature:", inspect.signature(method))
        print("Fetching:", TEST_URL)

        try:
            result = method(urls=[TEST_URL])

            if inspect.isawaitable(result):
                result = await result

        except Exception as exc:
            print("Fetch call failed:", repr(exc))
            print("Use the displayed signature to adjust the call.")
            return

        data = to_jsonable(result)

        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        output = FIXTURES_DIR / "fetch_article.json"
        output.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        print(f"Response saved to: {output}")
        print("Response type:", type(result).__name__)
        print("Response preview:")
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str)[:3000])

    finally:
        close = getattr(client, "close", None)
        if close:
            value = close()
            if inspect.isawaitable(value):
                await value


if __name__ == "__main__":
    asyncio.run(main())
