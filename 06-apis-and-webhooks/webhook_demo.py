"""Lesson 06 demo: APIs and webhooks with only the Python standard library.

Starts a local webhook receiver on your own machine, signs a payload the way
a real provider (Stripe, a CRM, a form tool) would, sends it, and shows the
receiver verifying the signature before acting on the event.

Fully offline. Nothing leaves localhost. No API keys.

Run:  python3 webhook_demo.py
"""

import hashlib
import hmac
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# In production this lives in an environment variable or a secrets manager,
# never in the code. It is hardcoded here so the demo runs with zero setup.
SECRET = b"lesson-secret"
URL = "http://127.0.0.1:8765/webhooks/leads"

received_events = []


def sign(payload: bytes, secret: bytes = SECRET) -> str:
    """Providers sign the raw body so the receiver can prove it is genuine."""
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


class WebhookReceiver(BaseHTTPRequestHandler):
    """The 'API' side of the demo: an HTTP endpoint that accepts events."""

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length)
        signature = self.headers.get("X-Signature", "")

        # Verify FIRST, parse second. Never act on an unverified webhook.
        if not hmac.compare_digest(signature, sign(body)):
            self.send_response(401)
            self.end_headers()
            print("receiver: REJECTED a request with a bad signature (HTTP 401)")
            return

        event = json.loads(body)
        received_events.append(event)
        print(
            f"receiver: accepted event '{event['type']}' "
            f"for lead {event['data']['lead_id']} (HTTP 200)"
        )
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):  # keep the demo output clean
        pass


def send_event(event: dict, secret: bytes = SECRET) -> int:
    """The 'provider' side: serialize, sign, POST, return the status code."""
    body = json.dumps(event).encode()
    request = urllib.request.Request(
        URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Signature": sign(body, secret),
        },
    )
    with urllib.request.urlopen(request) as response:
        return response.status


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8765), WebhookReceiver)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print("receiver: listening on http://127.0.0.1:8765/webhooks/leads")

    event = {
        "type": "lead.created",
        "data": {
            "lead_id": "LP-2026-00042",
            "name": "Ayesha Khan",
            "source": "website form",
        },
    }

    print(f"sender:   POST lead.created -> HTTP {send_event(event)}")

    try:
        send_event(event, secret=b"wrong-secret")
    except urllib.error.HTTPError as error:
        print(f"sender:   POST with the wrong secret -> HTTP {error.code}")

    server.shutdown()
    print(f"done: {len(received_events)} verified event(s) stored")


if __name__ == "__main__":
    main()
