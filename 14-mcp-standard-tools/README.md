# Lesson 14: MCP: giving agents standard tools

**Time:** 75-90 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 12 and 13 (tool calling, tool design)

In Lessons 12 and 13, the tools lived inside your program, wired to one model by your own code. That works until the second program wants the same tools, or a third team publishes tools you want to use. Then everyone is writing one-off integrations, M programs times N tools.

The Model Context Protocol (MCP) is the standard that removes that multiplication. A tool author packages tools once, as an MCP server. Any MCP client (Claude, ChatGPT, Cursor, your own agent) can connect, discover the tools at runtime, and call them. Write once, use from every client. This lesson builds a working miniature of the protocol so the shape is concrete, then points you at the real SDK and a production server design.

## What does an MCP exchange actually look like?

Four ideas carry the whole protocol:

1. **Transport.** A local server is a program the client launches, talking over the server's standard input and output (stdio). A remote server is reached over HTTP. The messages are the same either way.
2. **Messages.** Requests and responses are JSON-RPC 2.0: every request has an `id`, a `method`, and `params`; every response carries the same `id` and either a `result` or an `error`.
3. **Handshake and discovery.** The client sends `initialize`, the server replies with its name, version, and capabilities. Then the client sends `tools/list`, and the server describes every tool it offers: name, description, and a JSON Schema for its arguments: the same contract idea as Lesson 13, now standardised.
4. **Calls.** The client sends `tools/call` with a tool name and arguments; the server runs its own code and returns the result as content. The client never imports the server's code. It does not even need to know what language the server is written in.

Real MCP also covers resources (readable data), prompts (reusable templates), notifications, and more. Tools are the core you will use daily.

## The worked example: a teaching model

`mcp_server.py` is a complete miniature server in about 120 lines. It reads newline-delimited JSON from stdin, handles `initialize`, `ping`, `tools/list`, and `tools/call`, and serves two tools from a tiny lead pipeline: `capture_lead` and `score_lead`. `mcp_client.py` launches the server as a subprocess, performs the handshake, discovers the tools, and calls both.

Be clear about what this is: **a teaching model of the protocol, not the protocol.** It omits capability negotiation detail, resources, prompts, sampling, progress notifications, and the HTTP transport, and its error codes are simplified. What it preserves is the architecture, and the architecture is the lesson: discovery at runtime, tools as described data, the server owning its code.

### How to run it

```bash
cd 14-mcp-standard-tools
python3 mcp_client.py
```

Expected output:

```text
Connected to mini-pipeline-server v0.1.0
Discovered 2 tools:
  - score_lead: Score a lead 0-100 from budget, timeline, and decision authority. (needs: budget_usd, timeline_days, is_decision_maker)
  - capture_lead: Store a new lead in the pipeline and return its id. (needs: name, email, need)

capture_lead -> {"captured": {"id": "LP-001", "name": "Amara", "email": "amara@example.com", "need": "AI booking assistant for a dental clinic"}, "total_leads": 1}
score_lead   -> {"score": 100, "band": "hot"}
```

The moment to notice: the client printed the tool list it **discovered**, not a list it was coded with. Add a tool to the server and the same client sees it on the next run (the exercise makes you prove this). That is the property that makes an ecosystem possible.

## The real thing: SDKs and a production design

In production you do not hand-roll JSON-RPC. You use an SDK: the official Python SDK (`mcp`, with FastMCP for a decorator-style server), or the TypeScript SDK, and the SDK handles transports, validation, and protocol details. Your job shrinks to writing tool functions with good schemas, which is Lesson 13 again.

For a full production design, study TechAura's open-source LeadPipe MCP (linked below), built for the exact problem this lesson miniaturises: giving businesses without a CRM a scored, bookable lead pipeline. The design decisions worth stealing are not code, they are policies: a demo mode that runs offline with fake data so anyone can try the server safely; write modes (direct, dry-run, approval) so an agent can prepare changes without committing them; and approval as the default when real credentials are attached. A tool server that can write to a real calendar needs the same care as Lesson 13's booking tool, squared.

## Why this matters in production

MCP changes who your tools are for. A tool you write for your own agent can, with no extra integration work, be used by a client's agent in a different framework on a different continent. That is distribution, and it cuts both ways: your agents can also consume the growing public ecosystem of servers instead of your team hand-building every integration. Teams that treat their internal tools as MCP servers early keep reusing them; teams that hard-wire tools into one agent rewrite them per project.

## Common failures

- **Hardcoding a tool list in the client.** Discovery exists so servers can evolve. Always work from `tools/list`.
- **Skipping the handshake.** Clients that jump straight to `tools/call` break against real servers that enforce initialisation order.
- **Treating the teaching model as the spec.** Build intuition here, then read the actual specification before shipping. Protocol details (versions, capability flags) matter for interoperability.
- **Giant, vague tools, again.** MCP standardises transport, not design. Lesson 13's rules still decide whether models use your tools well.
- **Servers that demand credentials to do anything.** A demo or read-only mode lets people evaluate your server safely; it is also how servers get adopted.

## Recap

- [ ] MCP standardises how clients discover and call tools, so one server serves every client.
- [ ] The exchange is JSON-RPC: `initialize`, `tools/list`, `tools/call`, over stdio or HTTP.
- [ ] Clients discover tools at runtime; they never import server code.
- [ ] In production, use the official SDKs; your work is tool design, not protocol plumbing.
- [ ] Production servers need safety policies: demo mode, dry-run, and approval-first writes.

## Resources

- Model Context Protocol, official documentation: https://modelcontextprotocol.io
- MCP specification: https://modelcontextprotocol.io/specification/latest
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Case study, LeadPipe MCP (production server design by TechAura): https://github.com/techaurah/leadpipe-mcp
- MCP Registry (find published servers): https://registry.modelcontextprotocol.io
