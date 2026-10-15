
from urllib.parse import urlparse


# Initial source-priority rules for TruthLens.
# Tier 1 = highest priority; Tier 4 = lowest priority.
# These tiers are heuristics, not proof of accuracy.

TIER_WEIGHTS = {
    1: 1.0,
    2: 0.8,
    3: 0.5,
    4: 0.2,
}

# Official Indian government domains.
TIER_1_DOMAINS = {
    "india.gov.in",
    "pib.gov.in",
    "pmindia.gov.in",
    "mea.gov.in",
    "mib.gov.in",
    "mha.gov.in",
    "education.gov.in",
    "mospi.gov.in",
    "eci.gov.in",
    "supremecourtofindia.nic.in",
}

# Established news organizations.
# This list is a starting point, not an endorsement of every article.
TIER_2_DOMAINS = {
    "bbc.com",
    "bbc.co.uk",
    "reuters.com",
    "apnews.com",
    "thehindu.com",
    "indianexpress.com",
    "ndtv.com",
}

# Domains that do not match a known rule default to Tier 3.
# Tier 4 is reserved for explicitly configured low-priority sources.
TIER_4_DOMAINS = set()


def normalize_domain(url: str) -> str:
    """Extract a normalized hostname from an HTTP(S) URL."""

    if not isinstance(url, str) or not url.strip():
        return ""

    try:
        parsed = urlparse(url.strip())

        if parsed.scheme.lower() not in {"http", "https"}:
            return ""

        if not parsed.hostname:
            return ""

        host = parsed.hostname.lower().rstrip(".")

        # Treat www.example.com and example.com consistently.
        if host.startswith("www."):
            host = host[4:]

        return host

    except (ValueError, TypeError):
        return ""


def _matches_domain(host: str, domain: str) -> bool:
    """Match a domain and its subdomains without partial-name collisions."""

    return host == domain or host.endswith("." + domain)


def normalize_organization(url: str) -> str:
    """Group related hostnames under a common source organization."""

    host = normalize_domain(url)

    if not host:
        return ""

    # PIB's main website and its static subdomain
    # should count as one source organization.
    if host == "pib.gov.in" or host.endswith(".pib.gov.in"):
        return "pib.gov.in"

    return host



def classify_source(url: str) -> dict:
    """Classify a source using the configured domain rules."""

    host = normalize_domain(url)

    if not host:
        return {
            "url": url,
            "domain": None,
            "tier": 4,
            "weight": TIER_WEIGHTS[4],
            "reason": "Invalid or unsupported URL",
        }

    if any(_matches_domain(host, d) for d in TIER_1_DOMAINS):
        tier = 1
        reason = "Recognized official government domain"

    elif any(_matches_domain(host, d) for d in TIER_2_DOMAINS):
        tier = 2
        reason = "Recognized news organization domain"

    elif any(_matches_domain(host, d) for d in TIER_4_DOMAINS):
        tier = 4
        reason = "Explicitly configured low-priority domain"

    else:
        tier = 3
        reason = "Unclassified domain; reliability not yet assessed"

    return {
        "url": url,
        "domain": host,
        "tier": tier,
        "weight": TIER_WEIGHTS[tier],
        "reason": reason,
    }


def rank_sources(urls: list[str]) -> list[dict]:
    """Classify and rank URLs, preserving input order for equal tiers."""

    if not isinstance(urls, list):
        raise TypeError("urls must be a list of strings.")

    results = [classify_source(url) for url in urls]

    return sorted(
        results,
        key=lambda item: item["tier"],
    )
