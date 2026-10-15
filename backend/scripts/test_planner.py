
import json

from app.pipeline.planner import generate_queries


def main():
    claim = (
        "The government announced a nationwide school closure "
        "starting tomorrow."
    )

    print("Testing TruthLens planner...\n")

    result = generate_queries(claim)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
