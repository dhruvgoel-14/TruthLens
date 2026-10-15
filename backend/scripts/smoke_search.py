
import asyncio
import json
import inspect
from pathlib import Path

from tinyfish import TinyFish
from app.config import TINYFISH_API_KEY

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "tests" / "fixtures"


def save_json(filename: str, data: dict) -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURES_DIR / filename
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"Saved response: {path}")


async def main():
    print("TinyFish Search smoke test")
    print("SDK version: 0.9.0")

    client = TinyFish(api_key=TINYFISH_API_KEY)

    try:
        search = getattr(client, "search", None)
        print("Search object:", type(search).__name__)

        if search is None:
            print("This SDK client has no 'search' attribute.")
            print("Available client methods:")
            print([
                name for name in dir(client)
                if not name.startswith("_")
            ])
            return

        print("Search methods:")
        print([
            name for name in dir(search)
            if not name.startswith("_")
        ])

        query_method = getattr(search, "query", None)

        if query_method is None:
            print("No search.query method found.")
            return

        print("Search method signature:", inspect.signature(query_method))

        for language, query in [
            ("en", "official government news India"),
            ("hi", "भारत सरकार की आधिकारिक समाचार"),
        ]:
            print(f"\nTesting {language.upper()} search...")

            result = query_method(query=query)

            if inspect.isawaitable(result):
                result = await result

            if hasattr(result, "model_dump"):
                result = result.model_dump(mode="json")
            elif not isinstance(result, (dict, list, str, int, float, bool, type(None))):
                result = str(result)

            save_json(f"search_{language}.json", result)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str)[:1500])

    finally:
        close = getattr(client, "close", None)
        if close:
            result = close()
            if inspect.isawaitable(result):
                await result


if __name__ == "__main__":
    asyncio.run(main())
