# Exercise 30: Add the cascade

Routing sends each step to one model chosen in advance. A cascade makes the choice after a first attempt: run the cheap model, look at what it produced, and escalate to the frontier model only when the cheap answer smells wrong. It is the strategy most production systems end up with for their two or three hardest step types.

Work in a copy: `my_simulator.py`.

1. **Implement `run_cascade(day)`.** Start from the routed strategy (same routing table, no cache, no batch). For `draft` and `reason` steps only, run small-1 first. If the step's output is longer than a ramble threshold (draft: more than 320 output tokens; reason: more than 420), discard it and run the step again on frontier-1. Both runs count toward cost and latency: the cascade pays for its mistakes, which is exactly why it needs measuring.

2. **Report it in the same table.** Add a `cascade` row to the strategy table with day cost, average latency, and p95. Also print how many steps escalated, out of how many draft and reason steps ran. An escalation rate is a number you will tune in production; here you just have to be able to see it.

3. **Place it honestly.** Your cascade will probably land between `routed` and `all_small` on cost, and it should beat `routed` on the two hard step types' quality, though this simulator cannot measure quality (Lessons 24 and 25 can, against a real agent). Write one sentence in your solution notes about when a cascade beats plain routing, and one about when it does not.

Acceptance checks:
- The cascade row appears with the same workload (120 requests), and its cost is lower than `routed` and higher than `all_small`.
- The escalation count is printed and is greater than zero but well under half of the draft plus reason steps.
- Re-running produces identical numbers. If it does not, something in your version stopped being deterministic.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
