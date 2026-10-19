
from typing import Any, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


# Languages accepted from older clients. The backend now detects the claim's
# language itself, so this field is optional and ignored.
Language = Literal["en", "hi", "hinglish"]


class AnalyzeRequest(BaseModel):
    """Input supplied to the TruthLens analysis API."""

    model_config = ConfigDict(extra="forbid")

    claim: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The claim that TruthLens should investigate.",
    )

    language: Language | None = Field(
        default=None,
        deprecated=True,
        description=(
            "Deprecated and ignored. The claim's language is detected "
            "automatically."
        ),
    )

    max_sources: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of sources to fetch.",
    )

    @field_validator("claim")
    @classmethod
    def validate_claim(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Claim cannot be empty or whitespace only.")

        return value


class AnalyzeResponse(BaseModel):
    """Combined analysis result returned by TruthLens."""

    claim: str
    claim_en: str | None = None
    # One of: en, hi, hinglish, other. Reports saved before language detection
    # existed only have `language`.
    detected_language: str = "en"
    language: str | None = None

    verdict: str | None = None
    judge_verdict: str | None = None

    explanation: dict[str, Any] | None = None
    diff_segments: list[dict[str, Any]] = Field(default_factory=list)
    claim_vs_reality: dict[str, Any] | None = None

    zombie_suspected: bool = False
    escalation: dict[str, Any] | None = None

    consensus_score: float | None = None
    dominant_stance: str | None = None
    segments_valid: bool | None = None

    evidence: list[dict[str, Any]] = Field(default_factory=list)
    rejected_evidence: list[dict[str, Any]] = Field(default_factory=list)

    search_queries: list[str] = Field(default_factory=list)
    search_summary: dict[str, Any] | None = None
    sources: list[dict[str, Any]] = Field(default_factory=list)
    fetch_summary: dict[str, Any] | None = None
    evidence_chunks: list[dict[str, Any]] = Field(default_factory=list)

    timings_ms: dict[str, float] = Field(default_factory=dict)

    analysis_id: str | None = None
    escalation_available: bool = False

class CommunityClaim(BaseModel):
    """Summary card for a previously analyzed claim."""

    id: str
    claim: str
    verdict: str | None = None
    consensus_score: float | None = None
    explanation_snippet: str | None = None
    explanation_snippet_hi: str | None = None
    detected_language: str | None = None
    zombie_suspected: bool = False
    analysis_count: int = 1
    first_analyzed_at: datetime
    last_analyzed_at: datetime


class CommunityClaimsPage(BaseModel):
    items: list[CommunityClaim]
    page: int
    page_size: int
    total: int
    total_pages: int