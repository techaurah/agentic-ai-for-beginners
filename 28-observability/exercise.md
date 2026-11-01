# Exercise 28: Make the reader answer the money question per run

The lesson's reader totals cost by model, which answers "what did the day cost". The question an operator actually asks after an incident is narrower: "what did THAT run cost, and which runs are the expensive ones". Extend the reader to answer it.

Work in a copy: `my_trace_reader.py`. Run it from this lesson folder so the default trace path (`traces/day.jsonl`, written by `traced_agent.py`) resolves:

```bash
python3 traced_agent.py
python3 my_trace_reader.py
```

1. **Cost per run.** For every run, total its LLM tokens by model and price them with the same fake price table. Print one line per run: run id, job, status, total cost, and its single most expensive step.

2. **Tool reliability line.** After the model totals, print one line per tool: how many times it was called and how many of those calls failed, across all runs. Failed tool calls are where retries, and therefore surprise cost, come from.

3. **Flag the expensive runs.** Any run costing more than $0.01 gets the marker `<-- expensive` on its per-run line. The threshold is arbitrary and that is fine: production thresholds start arbitrary and get tuned by the first month of real bills.

Acceptance checks:
- The per-run costs add up to the same grand total the lesson's reader reports ($0.0209 on the seeded trace). If yours differs, one of the two readers is double-counting, and finding which is the exercise.
- The tool line shows `lookup_customer` called 3 times with 1 failure, matching run-003's timeline.
- run-003 is flagged expensive and run-002 is not.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
