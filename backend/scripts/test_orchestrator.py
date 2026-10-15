
import asyncio
import json

from app.pipeline.orchestrator import orchestrate_claim


async def main():
    claim = (
        "The Government of India publishes official press releases "
        "through the Press Information Bureau."
    )

    print("Running TruthLens orchestration...")

    result = await orchestrate_claim(
        claim=claim,
        language="en",
        max_sources=5,
    )

    print("\n=== ORCHESTRATION RESULT ===")
    print("Claim:", result["claim"])
    print("Final verdict:", result["verdict"])
    print("Gemini verdict:", result["judge_verdict"])
    print("Consensus score:", result["consensus_score"])

    print("\n=== STAGE TIMINGS ===")
    print(json.dumps(result["timings_ms"], indent=2))

    print("\n=== EVIDENCE SUMMARY ===")
    print("Sources:", len(result["sources"]))
    print("Evidence chunks:", len(result["evidence_chunks"]))
    print("Verified evidence:", len(result["evidence"]))
    print("Rejected evidence:", len(result["rejected_evidence"]))

    print("\nPASS: orchestration completed.")


if __name__ == "__main__":
    asyncio.run(main())
