# Exercise: add a FactCheck node

**Time:** about 35 minutes | **Difficulty:** Advanced

The Reviewer in `researcher_writer_graph.py` checks that every finding was used. It does not check that what the Writer wrote is actually supported by the finding it cites. A writer can cite the right source and still invent the claim, and fluent models do exactly this more often than any other kind of fabrication.

## Your task

Add a fourth node, `fact_check`, between the writer and the reviewer:

1. For each bullet in the brief, extract the claim text and the source title it cites (bullets in this lesson end with the source title in parentheses).
2. Check support: at least half of the claim's key words (content words, as in earlier lessons) should appear in the cited finding's text.
3. Write the verdict into state (`fact_check: pass/fail` plus notes naming any unsupported claim).
4. Add a conditional edge: on fail, route back to the writer once (respect the retry budget), with the unsupported claim named in the review notes.
5. Prove it works both ways: first run the honest pipeline and show a pass. Then simulate the classic failure (an invented, plausible statistic bolted onto a real citation) and show the node catching it and the rewrite removing it.

## What "done" looks like

- Honest brief: fact check passes, graph ends normally.
- Tampered brief: fact check fails with the unsupported claim named, one rewrite happens, second check passes.
- You can explain why support checking belongs in its own node rather than inside the reviewer.

The worked solution is in `solution/`. It uses the Lesson 20 support rule, which is deliberate: verification patterns should be reused across a system, not reinvented per agent.
