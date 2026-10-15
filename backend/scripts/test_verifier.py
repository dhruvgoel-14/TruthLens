
from app.pipeline.verifier import verify_judgment


def main():
    claim = "The government published the announcement."

    chunks = [
        {
            "chunk_id": 1,
            "source_url": "https://pib.gov.in/example",
            "domain": "pib.gov.in",
            "tier": 1,
            "tier_weight": 1.0,
            "text": "The government published the announcement yesterday.",
        },
        {
            "chunk_id": 2,
            "source_url": "https://news.example.org/example",
            "domain": "news.example.org",
            "tier": 3,
            "tier_weight": 0.5,
            "text": "The announcement was not published by the government.",
        },
    ]

    judge_output = {
        "diff_segments": [
            {
                "text": claim,
                "label": "TRUE",
                "correction": None,
                "evidence_chunk_ids": [1],
            }
        ],
        "evidence": [
            {
                "chunk_id": 1,
                "stance": "SUPPORTS",
                "verbatim_quote": "The government published the announcement yesterday.",
            },
            {
                "chunk_id": 2,
                "stance": "CONTRADICTS",
                "verbatim_quote": "This quote does not exist in the source.",
            },
            {
                "chunk_id": 999,
                "stance": "SUPPORTS",
                "verbatim_quote": "Fabricated evidence reference.",
            },
        ],
        "verdict": "SUPPORTED",
    }

    result = verify_judgment(
        judge_output=judge_output,
        evidence_chunks=chunks,
        original_claim=claim,
    )

    print("Segments valid:", result["segments_valid"])
    print("Consensus score:", result["consensus_score"])
    print("Dominant stance:", result["dominant_stance"])
    print("Final verdict:", result["final_verdict"])
    print("\nEvidence checks:")

    for item in result["evidence"]:
        print(
            "Chunk:", item["chunk_id"],
            "| Quote verified:", item["quote_verified"],
            "| Tier:", item["tier"],
        )

    print("\nRejected evidence:", result["rejected_evidence"])

    assert result["segments_valid"] is True
    assert result["evidence"][0]["quote_verified"] is True
    assert result["evidence"][1]["quote_verified"] is False
    assert len(result["rejected_evidence"]) == 1
    assert result["consensus_score"] == 100.0

    print("\nPASS: verifier checks completed.")


if __name__ == "__main__":
    main()
