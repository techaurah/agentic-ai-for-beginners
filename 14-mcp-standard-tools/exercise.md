# Exercise: grow the server, keep the client

The mini pipeline server offers two tools. A booking agent needs one more: `check_availability`, which takes a `date` (YYYY-MM-DD) and returns the free slots from a small fake calendar.

1. In `mcp_server.py`, add the tool the way the lesson's tools are built: one function, one entry in the `TOOLS` registry, and an `inputSchema` that requires `date`. Use this fake calendar: 2026-11-06 has 09:00, 10:30, 14:00; 2026-11-07 has 11:00; 2026-11-08 has none. A date outside the calendar returns an empty list with a note, not an error.
2. Do not touch the protocol handling (`handle`, `main`). If you think you need to, re-read how `tools/list` and `tools/call` find tools.
3. In `mcp_client.py`, change only the demo at the bottom: after connecting, call `check_availability` for 2026-11-06 before the existing two calls, and print the result.
4. Run the client.

**Done when:** the client reports "Discovered 3 tools", lists `check_availability` with its description and required field, and prints the three free slots for 2026-11-06. The `MiniMCPClient` class itself should be unchanged: if you edited it, explain to yourself why discovery failed you.

The worked solution is in `solution/` (full server and client files).
