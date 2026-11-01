# Solution: guarded stage moves and a hot-leads export

Run it with `python3 solution.py`. Output:

```text
loaded 3 leads
moved LP-2026-00031: qualified -> booked
rejected: illegal move contacted -> booked for LP-2026-00035; allowed: ['lost', 'qualified']
exported 1 hot lead(s) (score >= 80) to output/hot_leads.csv:
  LP-2026-00038  score 91  Daniel Smith (booked)
```

## What changed, and why

**The rules live in one function, `allowed_moves()`.** Given a current stage it returns the set of legal next stages: the next stage forward, plus `lost`. Every move in the system goes through that single gate, so when the business changes its pipeline rules, there is exactly one place to update, and no code path that quietly bypasses the rules. This is the same instinct as the signature check in Lesson 06: one choke point, checked first, that nothing routes around.

**The error message does the teaching.** A rejected move names the lead, the attempted move, and the allowed set. When an agent or a teammate hits this in production, the message tells them what to do instead, which is what a good validation error is for. Compare it with the alternative, a silent no-op, where the lead simply never moves and nobody knows why.

**The hot-leads export is a view, not a copy of state.** It filters and sorts at export time, so it can never drift out of sync with the pipeline. Views are cheap; duplicated state is a bug farm. The same principle produced `summary.csv` in the lesson: derived files are regenerated, never maintained by hand.
