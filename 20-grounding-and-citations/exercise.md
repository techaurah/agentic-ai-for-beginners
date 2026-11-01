# Exercise: catch the dropped negation

**Time:** about 30 minutes | **Difficulty:** Intermediate

Run `grounded_answers.py` and look at Answer B, claim 4:

> "We cover Manchester for emergency callouts." [S11]

S11 is the span that says Northbeam does **not** cover Manchester. The claim cites a real span, shares its key words, and contains no numbers, so rules R1 to R3 all pass it. The meaning is inverted and the checker is blind to it.

## Your task

Add a fourth rule to the checker, **R4: possible contradiction**, that flags this pattern:

1. For each claim, look at its cited spans.
2. If a cited span is negated (contains wording like "do not", "does not", "never", "no longer") and the claim itself is not negated, and the claim shares at least two key words with the span, flag the claim for review with the shared words listed.
3. R4 flags for human review instead of auto-failing. Word your output so a reviewer understands it is a suspicion, not a verdict.

Test your rule against three claims:

- "We cover Leeds and Harrogate" citing the positive area span: must NOT flag.
- "We cover Manchester for emergency callouts" citing the negated span: MUST flag.
- "We do not cover Sheffield" citing the negated span: must NOT flag, because the claim keeps the negation.

## What "done" looks like

- Exactly one flag, on the Manchester claim, with the shared words shown.
- You can explain why R4 is a review flag rather than a hard failure, in two or three sentences.

The worked solution is in `solution/`, using its own small span set (S10, S11) so the rule stays in focus.
