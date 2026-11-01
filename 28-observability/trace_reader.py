"""Read a trace file the way you will read one at 3am: timeline, then money.

Run it after traced_agent.py:

    python3 trace_reader.py            (reads traces/day.jsonl)
    python3 trace_reader.py other.jsonl

For each run it prints a timeline: every step with its offset from the
start of the run and its own duration, so a slow or failed step stands
out in the shape of the list before you read a single word. Then it
tallies the LLM calls by model and prices them.

The prices are FAKE, printed next to the table so nobody quotes them:
frontier-1 at $3.00 in / $15.00 out per million tokens, small-1 at
$0.15 / $0.60. Swap in your provider's real prices and the arithmetic,
which is the skill being taught, is identical.
"""

import json
import sys
from collections import defaultdict

PRICE_PER_MILLION = {
    "frontier-1": {"input": 3.00, "output": 15.00},
    "small-1": {"input": 0.15, "output": 0.60},
}


def describe(event):
    kind = event["event"]
    if kind == "llm_call":
        return (
            f"llm_call {event['model']} "
            f"({event['input_tokens']} in / {event['output_tokens']} out)"
        )
    if kind == "tool_call":
        mark = "" if event["ok"] else "  <-- FAILED"
        return f"tool_call {event['tool']}{mark}"
    return kind


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "traces/day.jsonl"
    events = [json.loads(line) for line in open(path, encoding="utf-8")]

    runs = {}
    order = []
    for event in events:
        run_id = event["run_id"]
        if run_id not in runs:
            runs[run_id] = []
            order.append(run_id)
        runs[run_id].append(event)

    totals = defaultdict(lambda: {"input": 0, "output": 0, "calls": 0})
    statuses = defaultdict(int)
    slowest = None

    for run_id in order:
        run_events = runs[run_id]
        start = run_events[0]["t_ms"]
        finish = run_events[-1]
        job = finish.get("job", "?")
        status = finish.get("status", "?")
        statuses[status] += 1
        print(
            f"RUN {run_id} ({job}) finished {status} "
            f"in {finish.get('total_ms', 0)}ms"
        )
        for event in run_events:
            offset = event["t_ms"] - start
            duration = event.get("duration_ms")
            suffix = f" [{duration}ms]" if duration else ""
            print(f"   t+{offset:>5}ms  {describe(event)}{suffix}")
            if event["event"] == "llm_call":
                bucket = totals[event["model"]]
                bucket["input"] += event["input_tokens"]
                bucket["output"] += event["output_tokens"]
                bucket["calls"] += 1
            if duration and (slowest is None or duration > slowest[0]):
                slowest = (duration, run_id, describe(event))
        print()

    print("Cost by model (fake prices, for teaching only):")
    grand = 0.0
    for model, bucket in sorted(totals.items()):
        prices = PRICE_PER_MILLION[model]
        cost = (
            bucket["input"] / 1_000_000 * prices["input"]
            + bucket["output"] / 1_000_000 * prices["output"]
        )
        grand += cost
        print(
            f"  {model:<11} {bucket['calls']} calls  "
            f"in {bucket['input']:,} tok  out {bucket['output']:,} tok  "
            f"${cost:.4f}"
        )
    summary = ", ".join(f"{n} {s}" for s, n in sorted(statuses.items()))
    print(f"Total estimated cost: ${grand:.4f} across {len(order)} runs ({summary})")
    if slowest:
        print(f"Slowest single step: {slowest[2]} in {slowest[1]} at {slowest[0]}ms")
    print()
    print("Read it like an operator: run-003 cost the most, took the")
    print("longest, and still ended escalated. The failed tool call and")
    print("its retry are visible in its timeline. That one run is where")
    print("this week's engineering time goes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
