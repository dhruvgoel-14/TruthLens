
from app.pipeline.domain_registry import (
    normalize_domain,
    classify_source,
    rank_sources,
)

# Both versions should normalize to the same domain.
assert normalize_domain("https://www.pib.gov.in/") == "pib.gov.in"
assert normalize_domain("https://pib.gov.in/") == "pib.gov.in"

# Both should receive Tier 1.
www_result = classify_source("https://www.pib.gov.in/")
plain_result = classify_source("https://pib.gov.in/")

assert www_result["tier"] == 1
assert plain_result["tier"] == 1
assert www_result["weight"] == plain_result["weight"] == 1.0

# Genuine subdomains should also match.
assert classify_source(
    "https://press.pib.gov.in/"
)["tier"] == 1

# Similar-looking unrelated domains must not match.
assert classify_source(
    "https://pib.gov.in.example.com/"
)["tier"] == 3

# Check that ranking keeps higher-priority sources first.
ranked = rank_sources([
    "https://example.com/",
    "https://www.pib.gov.in/",
    "https://www.reuters.com/",
])

assert [item["tier"] for item in ranked] == [1, 2, 3]

print("PASS: www and non-www domains normalize consistently.")
print("PASS: PIB domains receive Tier 1.")
print("PASS: Subdomains and unrelated domains are handled correctly.")
print("PASS: Source ranking works correctly.")
