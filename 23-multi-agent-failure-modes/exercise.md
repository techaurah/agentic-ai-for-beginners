# Exercise: stack the guards

**Time:** about 35 minutes | **Difficulty:** Advanced

In the lesson, the three guards live in separate demos. Production systems run them together, behind one checkpoint, because a single handoff can be a loop risk, a cost, and a future conflict at the same time.

## Your task

Build a `GuardStack` class that wraps all three guards behind one interface:

1. `check_handoff(artifact, action, cost)` runs the loop guard (state signature counting plus a turn budget) and the budget guard (cumulative spend) for every handoff, and returns whether the handoff may proceed.
2. `check_answer(answer, truth)` runs the arbiter comparison for outbound answers.
3. Every trip, from any guard, appends a structured escalation record (which guard, the reason, the context) to one shared log.
4. A `report()` method prints the escalation log plus totals: handoffs checked, tokens spent.

Then demonstrate the stack on three small pipelines: a planner/reviewer loop (loop guard trips), a 16-subtask decomposition against a 10,000 token budget (budget guard trips), and one confident wrong answer checked against the source of truth (arbiter trips).

## What "done" looks like

- One stack instance per pipeline catches its failure with a readable escalation entry.
- The escalation log entries share one shape, so an operator can scan all three the same way.
- You can explain one risk of stacking: for example, which guard should run first when a handoff is both over budget and looping, and why.

The worked solution is in `solution/`.
