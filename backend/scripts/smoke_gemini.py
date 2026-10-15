
import json

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


from app.config import GEMINI_API_KEY, GEMINI_MODEL


class SmokeTestResponse(BaseModel):
    claim: str
    verdict: str = Field(
        description="One of SUPPORTED, REFUTED, or INSUFFICIENT_EVIDENCE"
    )
    explanation: str
    evidence_needed: list[str]


def main():
    print("Gemini structured-output smoke test")

    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=(
                "Test claim: Water freezes at 0 degrees Celsius "
                "under standard atmospheric pressure. "
                "This is a schema and API test, not a live fact-check. "
                "Return the claim, a verdict, a short explanation, "
                "and a list of evidence needed."
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SmokeTestResponse,
                temperature=0,
            ),
        )

        parsed = response.parsed

        if parsed is None:
            if not response.text:
                raise RuntimeError(
                    "Gemini returned no parseable structured response."
                )
            parsed = SmokeTestResponse.model_validate_json(response.text)

        data = parsed.model_dump(mode="json")

        output = (
            Path(__file__).resolve().parents[1]
            / "tests"
            / "fixtures"
            / "gemini_structured.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Validate the saved JSON and expected schema.
        validated = SmokeTestResponse.model_validate_json(
            output.read_text(encoding="utf-8")
        )

        print("Gemini request succeeded.")
        print("Schema validation passed.")
        print(f"Saved fixture: {output}")
        print(json.dumps(validated.model_dump(), indent=2))

    finally:
        client.close()


if __name__ == "__main__":
    main()
