
import asyncio

from app.pipeline.evidence_pipeline import collect_evidence


async def main():
    claim = (
        "The Government of India publishes official press "
        "releases through the Press Information Bureau."
    )

    result = await collect_evidence(claim, max_sources=5)

    print("\n=== EVIDENCE PIPELINE TEST ===")
    print("Claim:", result["claim"])
    print("Queries generated:", len(result["search_queries"]))
    print("Search summary:", result["search_summary"])
    print("Sources selected:", len(result["sources"]))
    print("Fetch summary:", result["fetch_summary"])
    print("Evidence chunks:", len(result["evidence_chunks"]))

    print("\n=== SELECTED SOURCES ===")

    for source in result["sources"]:
        print(
            f"\nTitle: {source['title'] or 'Untitled'}"
            f"\nURL: {source['url']}"
            f"\nTier: {source['tier']}"
            f"\nWeight: {source['weight']}"
        )

    print("\n=== FIRST TWO EVIDENCE CHUNKS ===")

    for chunk in result["evidence_chunks"][:2]:
        print("\nSource:", chunk["source_url"])
        print("Language:", chunk["language"])
        print("Text:", chunk["text"][:500])
        print(f"Raw publication date: {chunk.get('date_raw')}")
        print(f"Normalized publication date: {chunk.get('date_abs')}")

    print("\n=== RANKED EVIDENCE ===")

    for chunk in result["evidence_chunks"][:5]:
        print(
            f"\nChunk ID: {chunk['chunk_id']}"
            f"\nDomain: {chunk.get('domain')}"
            f"\nTier: {chunk.get('tier')}"
            f"\nBM25 score: {chunk.get('bm25_score', 0):.4f}"
            f"\nTier weight: {chunk.get('tier_weight', 0):.2f}"
            f"\nRank score: {chunk.get('rank_score', 0):.4f}"
            f"\nText: {chunk['text'][:200]}"
        )


if __name__ == "__main__":
    asyncio.run(main())
