"""Send a signed fake WhatsApp message to your local webhook.

Use this to test the whole bot (pipeline + reply) even when Meta is not
delivering real messages to your app yet.

    python tools/simulate_whatsapp.py 918929044981 "Drinking warm water cures viral infections"

The first argument is YOUR WhatsApp number (digits only, with country code),
so the verdict is sent to your own phone. Run it from the backend folder.
Needs the backend running and WHATSAPP_APP_SECRET set in backend/.env.
"""

import hashlib
import hmac
import json
import sys
import time
import urllib.request
from pathlib import Path


def read_env(name: str) -> str:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return ""


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    number, text = sys.argv[1], " ".join(sys.argv[2:])
    url = "http://127.0.0.1:8000/api/whatsapp/webhook"

    secret = read_env("WHATSAPP_APP_SECRET")
    if not secret:
        sys.exit("WHATSAPP_APP_SECRET is missing from backend/.env")

    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "0",
            "changes": [{
                "field": "messages",
                "value": {"messages": [{
                    "id": f"wamid.SIM{int(time.time() * 1000)}",
                    "from": number,
                    "type": "text",
                    "text": {"body": text},
                }]},
            }],
        }],
    }

    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        print("Webhook answered:", response.status, response.read().decode())
    print("Now watch the backend terminal and your phone.")


if __name__ == "__main__":
    main()
