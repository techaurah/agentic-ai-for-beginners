# Lesson 02: Solution notes

Run it:

```bash
python3 landscape_quiz_extended.py
```

Expected output: the first three scenarios score exactly as in the lesson (6, 5, and 7 for their winners), then the clinic scenario lands on No-code automation with a score of 8: 3 for fixed steps, 3 for an operations team, and 2 from the new approval rule, followed by reasons that include the universal line about adding a human approval step before anything is sent.

**What changed and why.** The scenario dicts gain a `needs_human_approval` field, read with `.get()` so the older scenarios stay valid. The new rule does two different jobs and it is worth separating them: the +2 is a *capability* judgement (workflow tools genuinely ship approval nodes, frameworks make you build the gate), while the universal reason is a *safety* judgement that applies no matter which base wins. Good decision tools keep those apart: one changes the ranking, the other changes the design.

**What to notice.** If your prediction differed, check whether you scored the clinic's steps as varying. They do not: the judgement inside each draft is the model's, but the process shape is fixed, and shape is what the helper scores.
