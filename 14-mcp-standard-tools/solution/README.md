# Solution: the server grew, the client class did not

Run it (from this folder, so the client launches the solution server):

```bash
cd 14-mcp-standard-tools/solution
python3 mcp_client.py
```

Output:

```text
Connected to mini-pipeline-server v0.1.0
Discovered 3 tools:
  - score_lead: Score a lead 0-100 from budget, timeline, and decision authority. (needs: budget_usd, timeline_days, is_decision_maker)
  - capture_lead: Store a new lead in the pipeline and return its id. (needs: name, email, need)
  - check_availability: Return the free appointment slots for a date (YYYY-MM-DD). (needs: date)

check_availability -> {"date": "2026-11-06", "free_slots": ["09:00", "10:30", "14:00"], "note": "3 slot(s) free."}
capture_lead       -> {"captured": {"id": "LP-001", ...}, "total_leads": 1}
score_lead         -> {"score": 100, "band": "hot"}
```

## What to notice

- The server gained a tool by adding one function and one registry entry. `handle()` and the JSON-RPC plumbing are untouched, because dispatch goes through the registry.
- The `MiniMCPClient` class is identical to the lesson's. It printed and called a tool it had never heard of, because it learned the tool's name, description, and schema from `tools/list` at runtime. Only the demo script at the bottom of the client changed.
- This is the property that makes MCP an ecosystem rather than a pattern: server authors and client authors never coordinate releases. The contract is the discovery response.

Compare this with Lesson 12's exercise, where the same growth required a change inside the model. Both are valid architectures; the difference is who else can reuse the tool afterwards.
