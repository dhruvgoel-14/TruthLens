
import asyncio
import json

from app.pipeline.evidence_pipeline import collect_evidence
from app.pipeline.judge import judge_claim


async def main():
    claim = (
        "The Government of India publishes official press "
        "releases through the Press Information Bureau."
    )

    print("Collecting evidence...")

    research = await collect_evidence(claim, max_sources=5)

    if not research["evidence_chunks"]:
        print("No evidence chunks available; judge test cannot continue.")
        return

    print("Evidence chunks:", len(research["evidence_chunks"]))
    print("Calling Gemini judge...")

    result = await asyncio.to_thread(
        judge_claim,
        claim,
        research["evidence_chunks"],
        "en",
    )

    print("\n=== JUDGE RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
