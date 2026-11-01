# Solution: title boosting

Run it:

```bash
python3 solution.py
```

Output:

```
Q: What are your opening hours?
Without title boost: [('hours', 0.242), ('booking', 0.202), ('emergency', 0.163)]
With title boost:    [('hours', 0.678), ('hours', 0.392), ('booking', 0.096)]
```

## What changed

In `TfidfIndex.__init__`, the tokens indexed for each chunk are now the chunk's body tokens plus the document title's tokens repeated `title_boost` times (2 in the solution). One change, three effects:

1. The query word "hours" now matches strongly, because "Opening hours" is the title of exactly the right document.
2. Both chunks of the hours document rise, which is correct: both are about opening times.
3. The misleading chunks fall away. The emergency chunk scored well only because "24 hours" repeats in its body; it has no title support, so its relative rank drops.

## The general lesson

Retrieval quality is mostly decided before any model is involved, by what you put into the index. Production systems apply the same idea at larger scale: they index headings, product names, page titles, and sometimes a generated summary alongside the body text, and they weight those fields higher. When a RAG system gives wrong answers, check the index contents before touching the prompt.
