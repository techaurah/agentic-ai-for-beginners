"""The clinic agent as a small HTTP service, standard library only.

Run it:

    python3 server.py

Then, from another terminal:

    curl http://127.0.0.1:8000/health
    curl -X POST http://127.0.0.1:8000/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "How much is a cleaning?"}'

Configuration comes from the environment, never from edited code:
    PORT   port to listen on          (default 8000)
    HOST   interface to bind          (default 127.0.0.1; the Dockerfile
                                       sets 0.0.0.0, because a container
                                       that only listens on localhost
                                       cannot be reached from outside)

Design rules worth copying:
- /health exists and is cheap. Load balancers, container platforms, and
  your future 3am self all check it before anything else.
- Bad input is a 400 with a readable error, never a stack trace and
  never a crashed worker.
- Every request leaves exactly one log line with method, path, status,
  and intent. Lesson 28 turns these lines into proper traces.
- The agent (agent.py) knows nothing about HTTP. The server knows
  nothing about dentistry. That seam is where tests and swaps live.
"""

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agent import respond

SERVICE = {"service": "brightpath-front-desk", "version": "1.0.0"}


def log(line):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{stamp} {line}", flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "FrontDesk/1.0"

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", **SERVICE})
            log("GET /health 200")
        elif self.path == "/":
            self._send_json(200, {**SERVICE, "endpoints": ["/health", "/chat"]})
            log("GET / 200")
        else:
            self._send_json(404, {"error": f"no route for {self.path}"})
            log(f"GET {self.path} 404")

    def do_POST(self):
        if self.path != "/chat":
            self._send_json(404, {"error": f"no route for {self.path}"})
            log(f"POST {self.path} 404")
            return
        # API key check (exercise addition). The key comes from the
        # environment, never from code. When CLINIC_API_KEY is not set
        # the check is off: local development stays frictionless, and
        # that default is a deliberate decision, revisited at deploy
        # time by whoever sets the variable. /health is never checked;
        # the platform's health prober does not hold the key, and a
        # 401 there would get a healthy service restarted forever.
        expected_key = os.environ.get("CLINIC_API_KEY")
        if expected_key and self.headers.get("X-API-Key") != expected_key:
            self._send_json(401, {"error": "missing or invalid API key"})
            log("POST /chat 401")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b""
            data = json.loads(raw.decode("utf-8"))
            message = data["message"]
            if not isinstance(message, str) or not message.strip():
                raise ValueError("message must be a non-empty string")
        except (ValueError, KeyError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"bad request: {exc}"})
            log("POST /chat 400")
            return
        result = respond(message)
        self._send_json(200, result)
        log(f"POST /chat 200 intent={result['intent']}")

    def log_message(self, format, *args):
        # Silence the default stderr logger; log() above is our format.
        pass


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    log(f"{SERVICE['service']} v{SERVICE['version']} listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
