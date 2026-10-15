
from app.pipeline.domain_registry import normalize_organization

assert normalize_organization(
    "https://www.pib.gov.in/"
) == "pib.gov.in"

assert normalize_organization(
    "https://static.pib.gov.in/WriteReadData/file.pdf"
) == "pib.gov.in"

assert normalize_organization(
    "https://pib.gov.in/Allrel.aspx"
) == "pib.gov.in"

assert normalize_organization(
    "https://www.reuters.com/"
) == "reuters.com"

assert normalize_organization(
    "https://example.com/"
) == "example.com"

print("PASS: PIB-related hostnames share one organization ID.")
print("PASS: Unrelated organizations remain separate.")
