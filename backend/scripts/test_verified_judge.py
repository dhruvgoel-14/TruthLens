
import asyncio
import json

from app.pipeline.evidence_pipeline import collect_evidence
from app.pipeline.judge import judge_claim
from app.pipeline.verifier import verify_judgment


async def main():
    claim = (
        "The Government of India publishes official press "
        "releases through the Press Information Bureau."
    )

    print("=== STAGE 1: COLLECT EVIDENCE ===")

    research = await collect_evidence(claim, max_sources=5)
    chunks = research["evidence_chunks"]

    print("Searches succeeded:", research["search_summary"]["succeeded"])
    print("Pages fetched:", research["fetch_summary"]["fetched"])
    print("Ranked evidence chunks:", len(chunks))

    if not chunks:
        print("No evidence available. Stopping safely.")
        return

    print("\n=== STAGE 2: GEMINI JUDGMENT ===")

    judge_output = await asyncio.to_thread(
        judge_claim,
        claim,
        chunks,
        "en",
    )

    print("Judge verdict:", judge_output["verdict"])
    print("Evidence references:", len(judge_output["evidence"]))

    print("\n=== STAGE 3: DETERMINISTIC VERIFICATION ===")

    verified = verify_judgment(
        judge_output=judge_output,
        evidence_chunks=chunks,
        original_claim=claim,
    )

    print("Segments valid:", verified["segments_valid"])
    print("Consensus score:", verified["consensus_score"])
    print("Dominant stance:", verified["dominant_stance"])
    print("Final verdict:", verified["final_verdict"])

    print("\n=== EVIDENCE VALIDATION ===")

    for item in verified["evidence"]:
        print(
            f"Chunk {item['chunk_id']}: "
            f"stance={item['stance']}, "
            f"quote_verified={item['quote_verified']}, "
            f"tier={item['tier']}"
        )

    print("\n=== COMPLETE VERIFIED REPORT ===")
    print(json.dumps(verified, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
