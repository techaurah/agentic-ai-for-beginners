# Lesson 05: Solution notes

Run it:

```bash
python3 ticket_classifier.py
```

Expected output: the model returns `{"category": "billing", "confidence": "high", ...}`, the parse step reports OK (the JSON is syntactically valid), validation fails with "confidence is not a number: 'high'", one repair quoting that problem comes back with `0.92`, and the pipeline result routes the ticket as billing with numeric confidence.

**What changed and why.** The harness is the lesson's, transplanted: same contract, parse, validate, one repair flow, new job. The deliberate difference is where the failure lives. Lesson 05's flaw broke syntax, so the *parser* caught it. This flaw keeps syntax perfect and breaks a *type*, so only the validator catches it. Real model output fails both ways, and the type failure is the dangerous one in production, because systems that skip validation happily store the string "high" in a numeric column and break somewhere downstream, days later, somewhere unrelated.

**What to notice.** The validator also rejects booleans explicitly for confidence, because in Python `True` is an instance of `int` and would otherwise sneak through a numeric check as the value 1. Small print, real bug class. Validation code repays paranoia.
