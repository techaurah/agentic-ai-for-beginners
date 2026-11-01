# Exercise: make titles count

**Time:** about 25 minutes | **Difficulty:** Intermediate

Run the lesson code and ask it: "What are your opening hours?"

The right chunk (from the `hours` document) wins, but barely. The booking and emergency chunks score close behind, because the word "hours" does almost no work inside body text: the hours chunk talks about days and times, while the emergency chunk repeats "24 hours" and the booking chunk repeats "4 hours". In a bigger corpus, this question would regularly retrieve the wrong evidence.

## Your task

Improve the index so document titles count toward relevance:

1. In `rag.py`, change how chunk vectors are built so each chunk is indexed together with its document title, with the title terms given extra weight (for example, counted two or three times).
2. Re-run the opening-hours question and compare the top-3 scores before and after.
3. Re-run all five original questions and confirm none of them got worse: the top-ranked document for each should stay the same or improve.

## What "done" looks like

- The opening-hours question ranks an `hours` chunk first with a clearly wider margin than the unmodified code.
- The other four questions still retrieve the same top documents.
- You can explain, in two or three sentences, why metadata like titles and headings belongs in the indexed text.

Work in your own copy of `rag.py`. The worked solution is in `solution/` if you get stuck, but try the change yourself first: it is a small edit in the `TfidfIndex` class.
