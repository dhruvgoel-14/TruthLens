
import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required env var: {name}"
        )
    return value


TINYFISH_API_KEY = _require("TINYFISH_API_KEY")
GEMINI_API_KEY = _require("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "truthlens")

# Timeouts in seconds unless noted
PLANNER_TIMEOUT = 2.5
SEARCH_TIMEOUT = 2.5
FETCH_OUTER_TIMEOUT = 5.5
FETCH_PER_URL_TIMEOUT_MS = 4500
JUDGE_TIMEOUT = 40.0
AGENT_TIMEOUT = 45.0

# Source tier weights
TIER_WEIGHTS = {
    1: 1.0,
    2: 0.8,
    3: 0.5,
    4: 0.2,
}
