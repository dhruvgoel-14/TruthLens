"""WhatsApp Cloud API webhook for TruthLens.

Flow:
    user forwards a claim -> Meta -> POST /api/whatsapp/webhook (this file)
    -> TruthLens pipeline -> short verdict -> Graph API -> user

Meta calls the webhook, so it must be reachable over public HTTPS. The route
answers 200 immediately and does the (slow) analysis in a background task.
"""

import asyncio
import hashlib
import hmac
import logging
import os
import time
from collections import OrderedDict, defaultdict, deque
from uuid import uuid4

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.pipeline.orchestrator import orchestrate_claim

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

# --------------------------------------------------
# Configuration (all from environment variables)
# --------------------------------------------------

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
# Use the version shown in your Meta dashboard's sample request.
GRAPH_VERSION = os.getenv("WHATSAPP_GRAPH_VERSION", "v23.0")

# Optional: comma-separated wa_ids (digits only, with country code) allowed to
# use the bot. Empty means everyone.
ALLOWED_NUMBERS = {
    n.strip() for n in os.getenv("WHATSAPP_ALLOWED_NUMBERS", "").split(",") if n.strip()
}
RATE_LIMIT_PER_HOUR = int(os.getenv("WHATSAPP_RATE_LIMIT_PER_HOUR", "20"))

MAX_REPLY_CHARS = 1200  # WhatsApp allows 4096; keep replies short.

# In-memory state. Fine for one server process; use Redis/MongoDB if you scale
# to several instances.
_seen_message_ids: OrderedDict[str, None] = OrderedDict()
_recent_requests: dict[str, deque] = defaultdict(deque)

VERDICT_TEXT = {
    "SUPPORTED": ("✅", "Supported", "समर्थित"),
    "REFUTED": ("❌", "Refuted", "खंडित"),
    "MISLEADING": ("⚠️", "Misleading", "भ्रामक"),
    "INSUFFICIENT_EVIDENCE": ("❓", "Insufficient evidence", "अपर्याप्त प्रमाण"),
    "UNVERIFIED_NO_AUTHORITATIVE_SOURCES": ("❓", "Unverified", "असत्यापित"),
}

CHECKING_TEXT = "🔍 Checking this claim… / दावे की जांच हो रही है…"
HELP_TEXT = (
    "Send me a news headline, forwarded message or claim as text and I will "
    "fact-check it.\n\nकोई खबर या फॉरवर्ड किया हुआ संदेश टेक्स्ट में भेजें, मैं उसकी जांच करूंगा।"
)
ERROR_TEXT = "Sorry, I couldn't check this claim right now. Please try again.\n\nक्षमा करें, अभी जांच नहीं हो पाई। कृपया दोबारा कोशिश करें।"


# --------------------------------------------------
# Webhook verification (Meta calls this once when you save the webhook)
# --------------------------------------------------

@router.get("/webhook")
async def verify_webhook(
    mode: str | None = Query(default=None, alias="hub.mode"),
    token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    if not VERIFY_TOKEN:
        raise HTTPException(status_code=503, detail="WHATSAPP_VERIFY_TOKEN is not set.")

    if mode == "subscribe" and token and hmac.compare_digest(token, VERIFY_TOKEN):
        # Meta expects the challenge echoed back as plain text.
        return PlainTextResponse(challenge or "")

    raise HTTPException(status_code=403, detail="Verification failed.")


# --------------------------------------------------
# Incoming messages
# --------------------------------------------------

def _valid_signature(body: bytes, header: str | None) -> bool:
    """Check Meta's X-Hub-Signature-256 header against the raw request body."""
    if not APP_SECRET or not header or not header.startswith("sha256="):
        return False

    expected = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def _extract_messages(payload: dict) -> list[dict]:
    """Pull user messages out of Meta's nested webhook payload.

    Status updates (sent/delivered/read) arrive on the same webhook and are
    ignored here because they carry no `messages` list.
    """
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages.extend(value.get("messages", []) or [])
    return messages


def _remember(message_id: str) -> bool:
    """Return True if this message is new. Meta retries deliveries."""
    if message_id in _seen_message_ids:
        return False
    _seen_message_ids[message_id] = None
    while len(_seen_message_ids) > 5000:
        _seen_message_ids.popitem(last=False)
    return True


def _rate_limited(sender: str) -> bool:
    now = time.monotonic()
    window = _recent_requests[sender]
    while window and now - window[0] > 3600:
        window.popleft()
    if len(window) >= RATE_LIMIT_PER_HOUR:
        return True
    window.append(now)
    return False


@router.post("/webhook")
async def receive_webhook(request: Request, background: BackgroundTasks):
    body = await request.body()

    if not _valid_signature(body, request.headers.get("X-Hub-Signature-256")):
        logger.warning("WhatsApp webhook rejected: bad or missing signature")
        raise HTTPException(status_code=403, detail="Invalid signature.")

    try:
        payload = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON.")

    for message in _extract_messages(payload):
        message_id = message.get("id", "")
        sender = message.get("from", "")

        if not message_id or not sender or not _remember(message_id):
            continue
        if ALLOWED_NUMBERS and sender not in ALLOWED_NUMBERS:
            continue

        background.add_task(_handle_message, message)

    # Always acknowledge quickly; Meta retries if we are slow.
    return {"status": "ok"}


# --------------------------------------------------
# Handling one message
# --------------------------------------------------

def _claim_text(message: dict) -> str | None:
    kind = message.get("type")
    if kind == "text":
        return (message.get("text") or {}).get("body")
    if kind == "image":
        return (message.get("image") or {}).get("caption")
    return None


def _clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def format_reply(result: dict) -> str:
    """Short verdict message in the claim's own language."""
    verdict = result.get("final_verdict") or result.get("verdict") or ""
    emoji, label_en, label_hi = VERDICT_TEXT.get(
        verdict, ("❓", verdict.replace("_", " ").title(), verdict)
    )
    language = result.get("detected_language", "en")
    explanation = result.get("explanation") or {}

    if language == "hi":
        label = label_hi
        text = explanation.get("hi") or explanation.get("en")
    elif language == "hinglish":
        label = label_en
        text = explanation.get("original") or explanation.get("en")
    else:
        label = label_en
        text = explanation.get("en")

    footer = (
        "Automated check, not a final ruling. / स्वचालित जांच, अंतिम निर्णय नहीं।"
        if language != "en"
        else "Automated check, not a final ruling."
    )

    parts = [f"{emoji} *{label}*"]
    if text:
        parts.append(_clip(text, MAX_REPLY_CHARS))
    parts.append(f"_{footer}_")
    return "\n\n".join(parts)


async def send_text(to: str, body: str, reply_to: str | None = None) -> None:
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        logger.error("WhatsApp send skipped: access token or phone number ID missing")
        return

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:4000]},
    }
    if reply_to:
        payload["context"] = {"message_id": reply_to}

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            url, json=payload, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
        )

    if response.status_code >= 400:
        logger.error("WhatsApp send failed | %s | %s", response.status_code, response.text[:300])


async def _handle_message(message: dict) -> None:
    sender = message["from"]
    message_id = message["id"]
    claim = (_claim_text(message) or "").strip()

    if not claim or claim.lower() in {"hi", "hello", "help", "start", "namaste", "नमस्ते"}:
        await send_text(sender, HELP_TEXT, reply_to=message_id)
        return

    if _rate_limited(sender):
        await send_text(
            sender,
            "You have reached the hourly limit. Please try again later.\n\n"
            "आपकी प्रति घंटे की सीमा पूरी हो गई है। कृपया बाद में कोशिश करें।",
        )
        return

    await send_text(sender, CHECKING_TEXT, reply_to=message_id)

    analysis_id = str(uuid4())
    try:
        result = await asyncio.wait_for(orchestrate_claim(claim=claim), timeout=120)

        # Reuse the API's post-processing (stores the report in the community feed).
        from app.main import _finalize_result

        result = await _finalize_result(result, analysis_id)
        await send_text(sender, format_reply(result), reply_to=message_id)

    except ValueError:
        await send_text(sender, HELP_TEXT, reply_to=message_id)
    except Exception:
        logger.exception("WhatsApp analysis failed | id=%s", analysis_id)
        await send_text(sender, ERROR_TEXT, reply_to=message_id)
