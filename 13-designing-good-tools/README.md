# Lesson 13: Designing tools agents can actually use

**Time:** 60 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lesson 12 (the tool-calling loop)

Lesson 12 gave you a working loop. This lesson is about why some tools get used correctly almost every time and others fail in ways that look like model stupidity but are actually design faults. A model can only use a tool as well as the tool is described, validated, and protected against the realities of automated callers: retries, malformed arguments, and business rules the model cannot see.

Three design rules carry most of the weight. Each one is demonstrated in `tool_design.py` against a single realistic tool: `book_appointment`.

## Rule 1: What makes a schema a contract?

A schema is the agreement between the model and your code: these fields, these types, these allowed values. The lesson's schema says `service` must be one of `cleaning`, `checkup`, or `consultation`, and that `date`, `time`, `customer`, and an `idempotency_key` are all required.

The important part is what happens on a violation. The tool does not crash, and it does not guess. It returns a structured error that names the problem in language a model can act on: `'date' is required. Provide it and retry.` Models are surprisingly good at repairing their own calls when the error tells them exactly what to fix, and surprisingly bad when the error is a stack trace or a bare `400`.

Write your parameter descriptions the same way: say what the field is, what format it takes, and give an example. Every ambiguity you leave in a schema becomes a coin flip at runtime.

## Rule 2: Why should errors be data, not exceptions?

Consider the most common booking failure: the slot is already taken. That is not a malfunction. It is a normal answer the model needs in order to do its job ("that time is gone, offer another"). If the tool raises an exception, most loops either crash or swallow it, and the model either dies mid-conversation or invents a confirmation for a booking that never happened.

So in this lesson, tools return results in one envelope: `{"ok": True, "data": ...}` or `{"ok": False, "error": {"code", "message", "retryable"}}`. The `code` is for your logs and your code. The `message` is written for the model. The `retryable` flag separates "fix your arguments and try again" from "this will never work, tell the user something else". A `slot_taken` error even tells the model what to do next: check availability and offer a different slot.

## Rule 3: What is an idempotency key, and why do writes need one?

Networks time out. Loops retry. Models repeat themselves. Any of these can call your booking tool twice with the same request, and a naive tool books the customer twice.

An idempotency key is a unique string attached to a write request that means "this exact operation". The tool stores the key with the result. When the same key arrives again, the tool returns the stored result instead of doing the work a second time. Same input, same outcome, no duplicate. Payment APIs popularised this pattern; agents need it for the same reason, because an automated caller retries far more casually than a human clicking a button once.

### How to run it

```bash
cd 13-designing-good-tools
python3 tool_design.py
```

The demo runs five cases in order: a missing argument, an invalid enum value, a valid booking, an exact retry of that booking, and a different customer colliding with the same slot. Expected output:

```text
1. Missing argument (no date):
   {"ok": false, "error": {"code": "missing_argument", "message": "'date' is required. Provide it and retry.", "retryable": true}}
2. Invalid value (service not in the enum):
   {"ok": false, "error": {"code": "invalid_value", "message": "'service' must be one of ['cleaning', 'checkup', 'consultation'], got 'surgery'.", "retryable": true}}
3. Valid booking:
   {"ok": true, "data": {"booking_id": "BK-7144CE", "date": "2026-11-06", "time": "10:30", "service": "checkup", "customer": "Amara", "status": "confirmed"}}
4. The model retries the exact same request (network hiccup, retry loop):
   {"ok": true, "data": {"booking_id": "BK-7144CE", ..., "note": "Idempotent replay: this booking already existed."}}
   Bookings stored: 1 (still 1: no double booking)
5. A different customer tries the same slot with a new key:
   {"ok": false, "error": {"code": "slot_taken", "message": "2026-11-06 at 10:30 is already booked. Check availability and offer a different slot.", "retryable": true}}
```

Read case 4 and case 5 together: the same slot, two second attempts, opposite outcomes. The difference is the key. Case 4 is the same operation repeated, so it replays. Case 5 is a genuinely new operation, so it is judged on its merits and refused. That distinction is the entire concept.

## Why this matters in production

Tool design is where agent reliability is actually decided. Teams blame models for failures that trace back to a schema with a field called `data`, an error that said `invalid input`, or a write endpoint with no duplicate protection. The fixes are cheap and permanent: precise schemas, errors written for the caller, idempotent writes, and small tools with one clear job. In TechAura's own lead pipeline work, the booking step follows exactly these rules, because a double-booked appointment or a double-sent message is the kind of failure a client remembers.

## Common failures

- **Vague parameter names and descriptions.** `arg1`, `value`, `data` force the model to guess. Name the thing, state the format.
- **Accepting anything.** No validation means bad data reaches your database wearing a valid costume.
- **Exceptions as error handling.** A raised exception tells the model nothing and often ends the run.
- **Idempotency keys the caller invents per attempt.** A fresh key per retry defeats the mechanism. Keys must identify the operation, so retries of the same operation carry the same key (the exercise shows a version where the key is derived from the appointment itself).
- **Success responses that omit the result.** Return the created object, not just `{"status": "ok"}`, so the model can refer to real IDs instead of inventing them.

## Recap

- [ ] A schema is a contract: validate everything, and write errors that say how to fix the call.
- [ ] Errors are data with a code, a model-readable message, and a retryable flag.
- [ ] Business failures (slot taken) are normal answers, not exceptions.
- [ ] Every write tool takes an idempotency key; a retry replays the stored result.
- [ ] Return the created object so the model works with real identifiers.

## Resources

- Anthropic, Writing tools for agents: https://www.anthropic.com/engineering/writing-tools-for-agents
- OpenAI, Function calling guide: https://platform.openai.com/docs/guides/function-calling
- JSON Schema, getting started: https://json-schema.org/learn/getting-started-step-by-step
- IETF draft, The Idempotency-Key HTTP Header Field: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
