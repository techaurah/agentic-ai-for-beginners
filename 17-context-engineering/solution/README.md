# Solution: the right paragraph wins the budget

Run it:

```bash
cd 17-context-engineering/solution
python3 solution.py
```

Output:

```text
Question: What happens if I need to cancel the Friday cleaning?
Retrieval sub-budget: 60 tokens

  fee_policy         relevance 1  included
  cleaning_duration  relevance 1  dropped (over sub-budget)
  opening_hours      relevance 0  dropped (no keyword overlap)
  new_patients       relevance 0  dropped (no keyword overlap)
  parking            relevance 0  dropped (no keyword overlap)

Packed into the context, most relevant first:
  - Cancellations under 24 hours before the appointment incur a fee equal to half the service price. The fee is added to the next bill.
```

## The trap this exercise is built around

With plain exact-match keywords, the fee policy scores **zero** against the cancellation question: the question says "cancel", the policy says "cancellations", and exact matching sees two unrelated strings. The duration chunk wins on the single shared word "cleaning", and the agent answers a cancellation question with appointment-length information. Nothing crashes. The failure is silent and plausible, which is why it is worth meeting here.

The solution's prefix rule (words match if one is a prefix of the other, minimum length 4) is a toy fix, and the code says so. Production systems solve this with stemming, embeddings, hybrid search, and reranking models, in roughly that order of sophistication. The engineering lesson survives every one of those upgrades: someone must choose how retrieved text earns its place in the window, that choice must be visible in a report, and "whatever the search returned first" is a choice too, just a bad one.
