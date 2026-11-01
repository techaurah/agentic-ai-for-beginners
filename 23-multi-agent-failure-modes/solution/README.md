# Solution: the GuardStack

Run it:

```bash
python3 solution.py
```

Each pipeline trips its guard exactly once, and the three escalation logs read the same way:

```
Escalation log (1):
  [loop] state 5268c7752b seen 3 times by turn 5 | action=submit_for_review

Escalation log (1):
  [budget] next call would exceed the 10,000 token budget (spent 9,600) | action=execute

Escalation log (1):
  [arbiter] answer conflicts with the source of truth | answer='You can cancel free of charge up to 24 hours before the visit.'
```

## Design choices worth noticing

**Order matters.** `check_handoff` runs the budget guard before the loop guard. If a run is both looping and expensive, the budget trip is the one that saves money this second, and the loop will still be visible in the signature counts if the operator raises the budget and reruns. When two guards can trip on the same event, decide the order on purpose and write down why.

**One record shape.** Guard name, reason, context, for all three. An operator scanning a night of escalations should not need to learn three formats. This is the same contract discipline as Lesson 21, applied to your safety machinery instead of your agents.

**The stack is a class, not a framework.** About 60 lines. The value is not the code; it is that every handoff in the system passes one checkpoint, so there is exactly one place to add the next guard (a wall-clock limit and a per-agent error rate are the usual fourth and fifth) and exactly one log to alert on.
