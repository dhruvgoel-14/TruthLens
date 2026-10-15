
from app.pipeline.chunker import (
    normalize_text,
    tokenize,
    chunk_text,
    chunk_pages,
    rank_evidence_chunks,
)


def main():
    # 1. Unicode and Hindi tokenization
    hindi = "जंतर दिल्ली प्रतिबंध"

    assert normalize_text(hindi) == hindi
    assert tokenize(hindi) == ["जंतर", "दिल्ली", "प्रतिबंध"]

    print("PASS: Hindi tokenization")

    # 2. Chunk splitting and overlap
    text = " ".join(f"word{i}" for i in range(650))
    chunks = chunk_text(text, chunk_size=300, overlap=40)

    assert len(chunks) >= 3
    assert all(chunk.strip() for chunk in chunks)

    print("PASS: Chunk splitting")

    # 3. Numeric, unique chunk IDs
    fake_fetch = {
        "response": {
            "results": [
                {
                    "url": "https://pib.gov.in/example",
                    "title": "Official release",
                    "language": "en",
                    "text": (
                        "The government announced a public health "
                        "programme. The programme supports citizens. "
                    ) * 100,
                }
            ]
        }
    }

    evidence = chunk_pages(fake_fetch)

    ids = [chunk["chunk_id"] for chunk in evidence]

    assert ids == list(range(1, len(ids) + 1))

    print("PASS: Numeric and unique chunk IDs")

    # 4. Relevance ranking and tier weighting
    test_chunks = [
        {
            "chunk_id": 1,
            "source_url": "https://pib.gov.in/a",
            "text": "The government announced a public health programme.",
        },
        {
            "chunk_id": 2,
            "source_url": "https://example.org/b",
            "text": "A cricket team won its match yesterday.",
        },
        {
            "chunk_id": 3,
            "source_url": "https://news.example.com/c",
            "text": "The public health programme supports citizens.",
        },
    ]

    test_sources = [
        {
            "url": "https://pib.gov.in/a",
            "domain": "pib.gov.in",
            "tier": 1,
            "weight": 1.0,
        },
        {
            "url": "https://example.org/b",
            "domain": "example.org",
            "tier": 4,
            "weight": 0.2,
        },
        {
            "url": "https://news.example.com/c",
            "domain": "news.example.com",
            "tier": 3,
            "weight": 0.5,
        },
    ]

    ranked = rank_evidence_chunks(
        test_chunks,
        claim="The government announced a public health programme.",
        sources=test_sources,
        top_k=3,
    )

    assert ranked
    assert ranked[0]["chunk_id"] == 1
    assert all("rank_score" in item for item in ranked)

    print("PASS: BM25 and tier-weighted ranking")
    print("Ranked chunk IDs:", [item["chunk_id"] for item in ranked])


if __name__ == "__main__":
    main()
