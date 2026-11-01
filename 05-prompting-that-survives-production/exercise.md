# Lesson 05: Exercise

## Point the production pattern at a new job

Lead scoring was the lesson. Support triage is yours. Build `ticket_classifier.py` that applies the full pattern (contract, parse, validate, one repair) to this ticket:

"My card was charged twice for the March invoice and I need a refund."

Requirements:

1. **Contract:** reply with JSON only, keys `category` (one of billing, technical, account, other), `confidence` (a number from 0 to 1), `summary` (one short string).
2. **Few-shot:** include two worked examples in the prompt before the real ticket, one technical and one account case, in the same output shape.
3. **Validation:** the category must be in the allowed set, confidence must be a number (not a string) inside 0 to 1, and the summary must be a non-empty string. Write the checks so each failure names itself.
4. **One repair:** on a validation failure, send one repair request quoting the exact problem, then validate again. A second failure stops the script.
5. Use a fake client, labelled simulation, scripted in the spirit of the lesson: its first reply to your contract prompt should be JSON that *parses* but fails your validation. Choose the flaw yourself. If you cannot decide, make `confidence` arrive as the string "high".

The interesting design question: which of your checks fires on your scripted flaw, the parser or the validator? If your flaw is caught by the parser, pick a subtler one. Production's nastiest failures are the valid-looking ones.

## Solution

See `solution/ticket_classifier.py`, with notes in `solution/SOLUTION.md`.
