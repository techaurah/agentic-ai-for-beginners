"""Lesson 06 exercise solution: two event types, stored by type.

Extends webhook_demo.py: the receiver now accepts lead.created and
booking.confirmed, files each event under its type, and prints a count
by type at the end. Signature verification is unchanged and still first.

Run:  python3 solution.py
"""

import hashlib
import hmac
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = b"lesson-secret"
URL = "http://127.0.0.1:8765/webhooks/events"

store = {"lead.created": [], "booking.confirmed": []}


def sign(payload: bytes, secret: bytes = SECRET) -> str:
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length)
        if not hmac.compare_digest(self.headers.get("X-Signature", ""), sign(body)):
            self.send_response(401)
            self.end_headers()
            print("receiver: REJECTED a request with a bad signature (HTTP 401)")
            return
        event = json.loads(body)
        event_type = event["type"]
        if event_type not in store:
            self.send_response(400)
            self.end_headers()
            print(f"receiver: REJECTED unknown event type '{event_type}' (HTTP 400)")
            return
        store[event_type].append(event)
        print(f"receiver: stored '{event_type}' (HTTP 200)")
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def send_event(event: dict) -> int:
    body = json.dumps(event).encode()
    request = urllib.request.Request(
        URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "X-Signature": sign(body)},
    )
    with urllib.request.urlopen(request) as response:
        return response.status


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8765), Receiver)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print("receiver: listening on http://127.0.0.1:8765/webhooks/events")

    send_event({"type": "lead.created", "data": {"lead_id": "LP-2026-00042"}})
    send_event({"type": "lead.created", "data": {"lead_id": "LP-2026-00043"}})
    send_event(
        {"type": "booking.confirmed", "data": {"lead_id": "LP-2026-00042", "slot": "friday 14:00"}}
    )

    server.shutdown()
    print("stored events by type:")
    for event_type, events in store.items():
        print(f"  {event_type:<18} {len(events)}")


if __name__ == "__main__":
    main()
