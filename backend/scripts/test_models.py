
from pydantic import ValidationError

from app.models import AnalyzeRequest, AnalyzeResponse


def main():
    request = AnalyzeRequest(
        claim="  The Earth orbits the Sun.  ",
    )

    assert request.claim == "The Earth orbits the Sun."
    assert request.language == "en"
    assert request.max_sources == 5

    print("PASS: valid request")
    print("Normalized claim:", request.claim)

    try:
        AnalyzeRequest(claim="   ")
    except ValidationError:
        print("PASS: empty claim rejected")
    else:
        raise AssertionError("Whitespace-only claims should be rejected")

    try:
        AnalyzeRequest(claim="A claim", max_sources=50)
    except ValidationError:
        print("PASS: invalid source count rejected")
    else:
        raise AssertionError("Invalid source count should be rejected")

    response = AnalyzeResponse(
        claim=request.claim,
        language=request.language,
        verdict="SUPPORTED",
        timings_ms={"total": 10.0},
    )

    print("\nExample response:")
    print(response.model_dump_json(indent=2))

    print("\nPASS: model tests completed.")


if __name__ == "__main__":
    main()
