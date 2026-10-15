
from app.pipeline.domain_registry import normalize_domain, rank_sources


urls = [
    "https://www.pib.gov.in/",
    "https://pib.gov.in/Allrel.aspx",
    "https://pib.gov.in/About.aspx",
    "https://www.reuters.com/",
    "https://www.bbc.com/",
]

ranked = rank_sources(urls)

selected = []
domain_counts = {}
max_sources = 5
max_per_domain = 2

for source in ranked:
    domain = normalize_domain(source["url"])

    if domain_counts.get(domain, 0) < max_per_domain:
        selected.append(source)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    if len(selected) >= max_sources:
        break

assert len(selected) == 4
assert domain_counts["pib.gov.in"] == 2
assert domain_counts["reuters.com"] == 1
assert domain_counts["bbc.com"] == 1

print("PASS: No more than two URLs selected per domain.")
print("Selected domains:", [normalize_domain(s["url"]) for s in selected])
