
from datetime import datetime, timezone

from app.pipeline.dates import normalize_date
from app.pipeline.chunker import chunk_pages


def main():
    reference = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)

    print("=== DATE NORMALIZATION TESTS ===")

    cases = [
        ("7 hours ago", "2026-10-15"),
        ("3 days ago", "2026-10-12"),
        ("2 weeks ago", "2026-10-01"),
        ("2026-10-10", "2026-10-10"),
        ("not a date", None),
        (None, None),
    ]

    for raw_date, expected in cases:
        result = normalize_date(raw_date, reference_time=reference)
        print(f"{raw_date!r} -> {result['date_abs']!r}")
        assert result["date_abs"] == expected

    print("\n=== CHUNK DATE METADATA TEST ===")

    fake_fetch_response = {
        "response": {
            "results": [
                {
                    "url": "https://example.com/article",
                    "final_url": "https://example.com/article",
                    "title": "Example article",
                    "language": "en",
                    "published_date": None,
                    "text": (
                        "Published on October 10, 2026. "
                        "This is sample article content for testing."
                    ),
                },
                {
                    "url": "https://example.com/undated",
                    "title": "Undated article",
                    "language": "en",
                    "published_date": None,
                    "text": "This article does not contain a publication date.",
                },
            ]
        }
    }

    chunks = chunk_pages(fake_fetch_response)

    for chunk in chunks:
        print(
            f"Chunk {chunk['chunk_id']}: "
            f"date_raw={chunk.get('date_raw')!r}, "
            f"date_abs={chunk.get('date_abs')!r}"
        )

    assert chunks, "Expected at least one evidence chunk"
    assert chunks[0]["date_raw"] == "2026-10-10"
    assert chunks[0]["date_abs"] == "2026-10-10"
    assert chunks[1]["date_raw"] is None
    assert chunks[1]["date_abs"] is None

    print("\nPASS: Date normalization and chunk metadata tests completed.")


if __name__ == "__main__":
    main()
