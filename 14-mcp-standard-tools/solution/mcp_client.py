"""
Lesson 14 exercise solution: the client needed no new code to use the
new tool. It discovers check_availability at runtime through tools/list
and calls it the same way as every other tool. Only the demo script at
the bottom changed, which is precisely the benefit a standard protocol
buys you.

Run it:  python3 mcp_client.py   (from this solution/ folder)
"""

import json
import subprocess
import sys


class MiniMCPClient:
    def __init__(self, server_command: list[str]):
        self.proc = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, bufsize=1,
        )
        self._next_id = 1

    def request(self, method: str, params: dict | None = None) -> dict:
        req_id = self._next_id
        self._next_id += 1
        message = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params:
            message["params"] = params
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()
        response = json.loads(self.proc.stdout.readline())
        if "error" in response:
            raise RuntimeError(f"Server error: {response['error']['message']}")
        return response["result"]

    def notify(self, method: str) -> None:
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.proc.stdin.flush()

    def call_tool(self, name: str, arguments: dict) -> dict:
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        return json.loads(result["content"][0]["text"])

    def close(self) -> None:
        self.proc.stdin.close()
        self.proc.wait(timeout=5)


if __name__ == "__main__":
    client = MiniMCPClient([sys.executable, "mcp_server.py"])
    try:
        info = client.request("initialize")
        print(f"Connected to {info['serverInfo']['name']} v{info['serverInfo']['version']}")
        client.notify("notifications/initialized")

        tools = client.request("tools/list")["tools"]
        print(f"Discovered {len(tools)} tools:")
        for tool in tools:
            required = ", ".join(tool["inputSchema"]["required"])
            print(f"  - {tool['name']}: {tool['description']} (needs: {required})")

        availability = client.call_tool("check_availability", {"date": "2026-11-06"})
        print(f"\ncheck_availability -> {json.dumps(availability)}")

        lead = client.call_tool("capture_lead", {
            "name": "Amara", "email": "amara@example.com",
            "need": "AI booking assistant for a dental clinic"})
        print(f"capture_lead       -> {json.dumps(lead)}")

        score = client.call_tool("score_lead", {
            "budget_usd": 1500, "timeline_days": 10, "is_decision_maker": True})
        print(f"score_lead         -> {json.dumps(score)}")
    finally:
        client.close()
