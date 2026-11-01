"""Extended trace reader: per-run cost, tool reliability, expensive flags.

Solution to the Lesson 28 exercise. Run it from the lesson folder:

    python3 traced_agent.py
    python3 solution/trace_reader.py

Adds three things to the lesson's reader:

1. A cost line per run (tokens priced per model, summed per run), with
   the run's most expensive single step named.
2. A tool reliability table: calls and failures per tool, all runs.
3. An "<-- expensive" marker on any run over $0.01, because the first
   question after a bill arrives is always "which runs did that".

The per-run costs sum to the same grand total as the lesson reader.
Two views of one trace must reconcile, or one of them is lying.
"""

import json
import sys
from collections import defaultdict

PRICE_PER_MILLION = {
    "frontier-1": {"input": 3.00, "output": 15.00},
    "small-1": {"input": 0.15, "output": 0.60},
}
EXPENSIVE_THRESHOLD = 0.01


def step_cost(event):
    prices = PRICE_PER_MILLION[event["model"]]
    return (
        event["input_tokens"] / 1_000_000 * prices["input"]
        + event["output_tokens"] / 1_000_000 * prices["output"]
    )


def describe(event):
    if event["event"] == "llm_call":
        return (
            f"llm_call {event['model']} "
            f"({event['input_tokens']} in / {event['output_tokens']} out)"
        )
    if event["event"] == "tool_call":
        return f"tool_call {event['tool']}"
    return event["event"]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "traces/day.jsonl"
    events = [json.loads(line) for line in open(path, encoding="utf-8")]

    runs = {}
    order = []
    tool_stats = defaultdict(lambda: {"calls": 0, "failures": 0})
    for event in events:
        run_id = event["run_id"]
        if run_id not in runs:
            runs[run_id] = []
            order.append(run_id)
        runs[run_id].append(event)
        if event["event"] == "tool_call":
            stats = tool_stats[event["tool"]]
            stats["calls"] += 1
            if not event["ok"]:
                stats["failures"] += 1

    print("Cost per run (fake prices, same table as the lesson reader):")
    grand = 0.0
    for run_id in order:
        run_events = runs[run_id]
        finish = run_events[-1]
        run_cost = 0.0
        priciest = None
        for event in run_events:
            if event["event"] == "llm_call":
                cost = step_cost(event)
                run_cost += cost
                if priciest is None or cost > priciest[0]:
                    priciest = (cost, describe(event))
        grand += run_cost
        flag = "  <-- expensive" if run_cost > EXPENSIVE_THRESHOLD else ""
        print(
            f"  {run_id}  {finish.get('job', '?'):<18} "
            f"status {finish.get('status', '?'):<10} ${run_cost:.4f}{flag}"
        )
        if priciest:
            print(f"      most expensive step: {priciest[1]} at ${priciest[0]:.4f}")

    print()
    print("Tool reliability (all runs):")
    for tool, stats in sorted(tool_stats.items()):
        print(
            f"  {tool:<18} {stats['calls']} calls, "
            f"{stats['failures']} failures"
        )

    print()
    print(f"Grand total across {len(order)} runs: ${grand:.4f}")
    print("Check: this must equal the lesson reader's total. On the")
    print("seeded trace both say $0.0209. Two views, one trace, one number.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
