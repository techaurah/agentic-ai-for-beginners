# Lesson 05: Prompting that survives production

**Time:** about 50 minutes · **Difficulty:** Beginner · **Prerequisites:** Lesson 04

Your prompt worked twenty times in a notebook. Then it met a real Tuesday: an odd customer message, a tired model, a reply that is JSON except for one trailing comma. The workflow that trusted it did not crash loudly. It quietly routed nothing, and the lead sat unanswered until a human noticed on Friday. Demo prompting and production prompting differ by exactly one assumption. Demo prompting assumes the model will comply. Production prompting assumes it will not, and builds the harness that copes.

## What is an output contract?

An output contract is the part of your prompt written like an API specification instead of a request: the exact keys, their types, their allowed ranges, and nothing else in the reply. "Reply with JSON only, keys score (integer 0-100) and reason (one short string)" is a contract. "Please give me a score, JSON if possible, thanks" is a wish. Contracts also carry your business rules in the open: what 80 means, what 65 means, what counts as evidence. A reviewer can read the contract and audit the behaviour, which is more than can be said for most prompts in the wild.

## Why do examples beat longer instructions?

A **few-shot example** is a worked input and output pair inside the prompt. Two of them anchor a model harder than a paragraph of adjectives, because they show the shape of a good answer, the length of a good reason, and the standard for borderline calls. They are also where your judgement gets encoded: pick examples that include one clear case and one tempting wrong case, and the model inherits the distinction. When behaviour drifts in production, the fix is often a better example, not a louder instruction.

## Why validate if you asked properly?

Because the model is probabilistic, compliance is a rate, not a guarantee. Validation converts hope into a gate. Parse the reply as JSON (syntax). Check every key exists, check types, check ranges, check membership in allowed sets (semantics). The exercise for this lesson is built around the difference: a reply can be perfectly valid JSON and still carry a confidence of "high" where your code needs a number between 0 and 1. Syntax checks wave it through. Type checks catch it. Downstream code only ever sees data that passed both.

## What is a repair loop, and when does it stop?

When validation fails, the strongest cheap fix is one repair request: send the model its own bad reply's error, in words ("your previous reply was not valid JSON, error: expecting property name, reply with JSON only"), and let it correct itself. One. Not five. A bounded repair turns a common failure into a non-event; an unbounded one turns it into a cost spiral and, occasionally, an infinite loop. After one failed repair, the professional move is escalation: route the item to a human or a holding queue, and keep the bad reply. That failed reply is gold later; it belongs in your evaluation set (Lesson 25).

## The worked example: score a lead, three ways

The file `prompting_production.py` scores the Bright Smiles Dental enquiry from Lesson 04 with a scripted fake client. Attempt 1 sends a fragile prompt and gets flowing prose: nothing to parse, pipeline dead. Attempt 2 sends the production prompt (scoring rules, two few-shot examples, the contract) and gets JSON with a trailing comma, the most common way real models break strict parsers. The harness then makes exactly one repair request quoting the parse error, receives clean JSON, validates it, and computes the routing band in code. Note that last move: the band (HOT at 80+, WARM at 65+, NURTURE below) is derived by a function, never requested from the model. Derived values are code's job.

Run it:

```bash
cd 05-prompting-that-survives-production
python3 prompting_production.py
```

Expected output (the exact column number in the JSON error can vary by Python version; the shape will not):

```text
ATTEMPT 1: the fragile prompt
  Model said: Honestly this lead looks hot. They are clearly losing bookings, Dana sounds ready to buy, and I would score it around 85 out of 100.
  Parse result: FAILED. Prose cannot be parsed as JSON.
  Pipeline result: nothing usable. A workflow stops here.

ATTEMPT 2: the production prompt
  Model said: {"score": 85, "reason": "Urgent and specific need, named decision maker, weekly losses stated",}
  Parse result: FAILED (Expecting property name enclosed in double quotes: line 1 column 96 (char 95)).
  One repair attempt, quoting the error back to the model:
  Model said: {"score": 85, "reason": "Urgent and specific need, named decision maker, weekly losses stated"}
  Validation: OK (score in range, reason present)
  Pipeline result: {'score': 85, 'band': 'HOT', 'reason': 'Urgent and specific need, named decision maker, weekly losses stated'}
  The workflow can now route this lead on its own.
```

## Why this matters in production

This five-part pattern (contract, parse, validate, one repair, derive in code) is the most reused shape in the whole course. Tool calling (Lessons 12 and 13) is this pattern aimed at actions. Grounded answers (Lesson 20) are this pattern aimed at citations. Evaluation (Lessons 24 and 25) is this pattern turned on the system itself. Learn it here, on a lead score, where the stakes are imaginary, and you will recognise it everywhere the stakes are real. The unglamorous truth of production AI is that reliability lives in harnesses like this one, not in cleverer prompts.

## Common failures

- **Begging instead of contracting.** Capital letters and pleading do not move compliance rates. Specifications and examples do.
- **Retrying forever.** An unbounded loop converts one bad reply into an outage and a bill. One repair, then escalate.
- **Trusting the model's derived labels.** If the model returns both a score and a band, they will eventually disagree. Compute the band.
- **Throwing away failures.** The raw bad reply is diagnostic evidence and future test data. Log it with the input that caused it.

## Recap checklist

- [ ] I can write an output contract: keys, types, ranges, reply shape
- [ ] I can explain what few-shot examples anchor, and pick two good ones
- [ ] I can separate syntax validation from type and range validation
- [ ] I know the repair rule: quote the error, retry once, then escalate
- [ ] I compute derived values in code, always

## Resources

- [Prompt engineering overview, Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview): a major provider's full prompting curriculum, free
- [Prompt engineering guide, OpenAI](https://platform.openai.com/docs/guides/prompt-engineering): the other major provider's tactics, useful to compare against Anthropic's
- [json, Python documentation](https://docs.python.org/3/library/json.html): the parser this lesson leans on, including its error types
- [JSON.org](https://www.json.org/json-en.html): the format's own one-page specification, worth reading once in your life

**Next:** Module 2 begins. Lesson 06, APIs and webhooks: how agents touch the real world.
