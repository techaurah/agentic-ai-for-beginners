"""
Lesson 14 exercise solution: the teaching-model server with a third
tool, check_availability, added exactly the way you would add a tool to
a real MCP server: one function, one registry entry, one schema.
Nothing in the protocol handling changes.

Run via the client:  python3 mcp_client.py
"""

import json
import sys

LEADS = []
FAKE_CALENDAR = {
    "2026-11-06": ["09:00", "10:30", "14:00"],
    "2026-11-07": ["11:00"],
    "2026-11-08": [],
}


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


def check_availability(args: dict) -> dict:
    date = args["date"]
    if date not in FAKE_CALENDAR:
        return {"date": date, "free_slots": [],
                "note": "No calendar data for this date."}
    slots = FAKE_CALENDAR[date]
    return {"date": date, "free_slots": slots,
            "note": f"{len(slots)} slot(s) free."}


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
    "check_availability": {
        "fn": check_availability,
        "description": "Return the free appointment slots for a date (YYYY-MM-DD).",
        "inputSchema": {
            "type": "object",
            "properties": {"date": {"type": "string"}},
            "required": ["date"],
        },
    },
}


def handle(request: dict) -> dict | None:
    method = request.get("method")
    req_id = request.get("id")
    if req_id is None:
        return None

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
