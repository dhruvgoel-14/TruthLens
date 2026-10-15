
import asyncio
import inspect
import json
from pathlib import Path

from tinyfish import TinyFish
from app.config import TINYFISH_API_KEY

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "tests" / "fixtures"

TEST_URL = "https://www.india.gov.in/"


def to_jsonable(result):
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    if isinstance(result, (dict, list, str, int, float, bool, type(None))):
        return result
    return str(result)


async def main():
    print("TinyFish Agent smoke test")

    client = TinyFish(api_key=TINYFISH_API_KEY)

    try:
        agent = client.agent
        method = agent.run

        print("Agent run signature:", inspect.signature(method))
        print("Starting bounded task...")

        result = method(
            goal=(
                "Open the provided website and identify its official site name. "
                "Return the name and the homepage URL. Do not submit forms, "
                "log in, or make any changes."
            ),
            url=TEST_URL,
        )

        if inspect.isawaitable(result):
            result = await result

        data = to_jsonable(result)

        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        output = FIXTURES_DIR / "agent_run.json"
        output.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        print(f"Response saved to: {output}")
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
