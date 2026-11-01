# Exercise: retrieve by relevance, not by habit

The lesson's assembler packs one retrieved policy document in a fixed position. Real retrieval returns several chunks and a question that only one of them answers. Packing in a fixed order means a long, irrelevant chunk can consume the retrieval budget while the paragraph that answers the question is dropped.

Upgrade the retrieval part of the assembler:

1. Take the five chunks in `solution/`'s starting set (fee policy, cleaning duration, opening hours, new patient notes, parking) or write your own five, each a few sentences, on clearly different topics.
2. Score every chunk against the user's question. Start with keyword overlap after removing stopwords. Discover its weakness yourself: run it on the question "What happens if I need to cancel the Friday cleaning?" and watch what exact matching does with the words "cancel" and "cancellations". Fix the matching with a simple loose rule (the solution uses prefix matching) and note that embeddings and rerankers exist to solve this properly.
3. Pack chunks most-relevant-first under a retrieval sub-budget of 60 tokens. Chunks with zero relevance are dropped even if budget remains: irrelevant context is not neutral, it dilutes attention and costs money.
4. Print a report showing each chunk's relevance score and whether it was included, and why not if it was not.

**Done when:** for the cancellation question, the fee policy chunk is the one packed into the context, the report explains every other chunk's exclusion, and the total retrieval spend is within the 60-token sub-budget.

The worked solution is in `solution/`.
