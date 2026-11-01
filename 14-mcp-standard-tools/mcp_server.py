"""
Lesson 14: a minimal MCP-style server (TEACHING MODEL).

This is a teaching model of the Model Context Protocol, not the protocol
itself. It keeps the shape of real MCP:

  * Transport: newline-delimited JSON messages over stdio, exactly how a
    local MCP server is launched by a client.
  * Messages: JSON-RPC 2.0 style requests with an id, a method, and params.
  * Methods: initialize, tools/list, tools/call, ping.
  * Tools are described as data (name, description, inputSchema) and the
    server, not the model, owns and runs the tool code.

What it deliberately leaves out (the real protocol and SDKs add these):
capability negotiation detail, resources and prompts, sampling, progress
notifications, and the HTTP transport. The README explains the real SDK
path (Python: mcp package, FastMCP) and points at a production example.

Run the demo with the client, not this file directly:
    python3 mcp_client.py
"""

import json
import sys

# Two small tools in the shape of a lead pipeline (see the lesson README
# for how these map to the production LeadPipe MCP design).
LEADS = []


def score_lead(args: dict) -> dict:
    score = 0
    score += 40 if args["budget_usd"] >= 1000 else 20 if args["budget_usd"] >= 500 else 5
    score += 35 if args["timeline_days"] <= 14 else 20 if args["timeline_days"] <= 30 else 5
    score += 25 if args["is_decision_maker"] else 5
    band = "hot" if score >= 80 else "warm" if score >= 55 else "cold"
    return {"score": score, "band": band}


def capture_lead(args: dict) -> dict:
    lead = {"id": f"LP-{len(LEADS) + 1:03d}", "name": args["name"],
            "email": args["email"], "need": args["need"]}
    LEADS.append(lead)
    return {"captured": lead, "total_leads": len(LEADS)}


TOOLS = {
    "score_lead": {
        "fn": score_lead,
        "description": "Score a lead 0-100 from budget, timeline, and decision authority.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "budget_usd": {"type": "integer"},
                "timeline_days": {"type": "integer"},
                "is_decision_maker": {"type": "boolean"},
            },
            "required": ["budget_usd", "timeline_days", "is_decision_maker"],
        },
    },
    "capture_lead": {
        "fn": capture_lead,
        "description": "Store a new lead in the pipeline and return its id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "need": {"type": "string"},
            },
            "required": ["name", "email", "need"],
        },
    },
}


def handle(request: dict) -> dict | None:
    """Map one JSON-RPC request to a response (None for notifications)."""
    method = request.get("method")
    req_id = request.get("id")
    if req_id is None:
        return None  # notification: no response expected

    if method == "initialize":
        result = {"protocolVersion": "teaching-model-1",
                  "serverInfo": {"name": "mini-pipeline-server", "version": "0.1.0"},
                  "capabilities": {"tools": {}}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": name, "description": t["description"],
                             "inputSchema": t["inputSchema"]}
                            for name, t in TOOLS.items()]}
    elif method == "tools/call":
        params = request["params"]
        name = params["name"]
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": f"Unknown tool: {name}"}}
        output = TOOLS[name]["fn"](params.get("arguments", {}))
        result = {"content": [{"type": "text", "text": json.dumps(output)}],
                  "isError": False}
    else:
        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}}

    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle(json.loads(line))
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
