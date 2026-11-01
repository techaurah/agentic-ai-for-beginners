"""
Lesson 14: a minimal MCP-style client (TEACHING MODEL).

The client does what every MCP host does:
  1. Launches the server as a subprocess (stdio transport).
  2. Sends initialize, then tools/list to discover what the server offers.
  3. Calls tools with tools/call and reads the results.

Because discovery happens at runtime, this same client works with any
server that speaks the protocol. That is the entire point of MCP: write
the tool once, and every client can use it.

Run it:  python3 mcp_client.py
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

        lead = client.call_tool("capture_lead", {
            "name": "Amara", "email": "amara@example.com",
            "need": "AI booking assistant for a dental clinic"})
        print(f"\ncapture_lead -> {json.dumps(lead)}")

        score = client.call_tool("score_lead", {
            "budget_usd": 1500, "timeline_days": 10, "is_decision_maker": True})
        print(f"score_lead   -> {json.dumps(score)}")
    finally:
        client.close()
