# Exercise: guarded stage moves and a hot-leads export

`state_demo.py` checks that a stage *exists* before moving a lead, but it allows any jump: `new` straight to `booked`, or `booked` backwards to `contacted`. Real pipelines have rules, and agents must not be able to break them.

In a new file:

1. Define the legal moves: a lead may move **forward one stage at a time** (`new` to `contacted`, `contacted` to `qualified`, `qualified` to `booked`), or to `lost` from any stage except `lost` itself. Every other move must raise an error that names the lead, the attempted move, and what was allowed.
2. Load the seed pipeline from `data/pipeline_seed.json`.
3. Move `LP-2026-00031` from `qualified` to `booked` (legal), then attempt `LP-2026-00035` from `contacted` to `booked` (illegal) and catch and print the rejection.
4. Export every lead with a score of 80 or more to `output/hot_leads.csv` with columns `id, name, score, stage, service`, sorted by score descending, and print the exported leads.

Expected output shape:

```text
loaded 3 leads
moved LP-2026-00031: qualified -> booked
rejected: illegal move contacted -> booked for LP-2026-00035; allowed: ['lost', 'qualified']
exported 1 hot lead(s) (score >= 80) to output/hot_leads.csv:
  LP-2026-00038  score 91  Daniel Smith (booked)
```

When yours matches, read `solution/` for why the transition map, rather than a pile of if statements, is the shape worth keeping.
