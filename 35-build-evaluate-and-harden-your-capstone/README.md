# Lesson 35: Build, Evaluate, and Harden Your Capstone

**Time:** 90-120 minutes plus build time · **Difficulty:** Advanced · **Prerequisites:** Lesson 34 (capstone spec and scaffolding), Lesson 24 (testing agents), Lesson 25 (eval sets from real failures)

## The hook

Your capstone compiles, the demo runs, and the seed data behaves. None of that is evidence. The difference between a course project and a professional system is what happens on the second run, the duplicate message, the full calendar, and the day the extractor returns nonsense. This lesson gives you the instrument that finds those moments before a client does: an outcome eval suite. You will run it first against a deliberately broken assistant, read its failures like a professional, and then turn the same suite on your own build.

## What outcome evaluation means here

Lesson 24 set the principle: assert outcomes, not vibes. For this pipeline an outcome is small and checkable: for each enquiry, the band it landed in, the action taken, and, where the arithmetic matters, the exact score. Plus two system-level facts: how many outcomes exist at all, and how many bookings exist after the pipeline runs twice. No language model judges any of it. Every assertion is a comparison a script can make, which means the suite runs offline, in CI, in seconds, forever, for free.

The scenario format is JSON, one file, eight scenarios:

```json
{
  "name": "duplicate contact merges into one outcome",
  "slots": 5,
  "enquiries": [ "... two raw enquiries, same contact ..." ],
  "expected_total": 1,
  "expected_outcomes": { "S2-1": {"band": "HOT", "action": "booked", "score": 93} }
}
```

Three fields do heavy work. `expected_total` catches duplicates and silent drops, the two failures that produce no wrong row to inspect, only a wrong count. `score` in an expectation catches clamping and arithmetic bugs that band checks would wave through. `runs` and `expected_bookings_after_all_runs` catch the failure that only exists in time: the second run.

## Worked example: the specimen

This lesson ships `sample_assistant.py`, a plausible first attempt with five real defects, and `eval_harness.py`. Run them:

```bash
python3 eval_harness.py
```

Real output:

```text
PASS  hot enquiry books a slot
FAIL  duplicate contact merges into one outcome
        - expected 1 outcome(s), got 2
        - S2-1: expected score 93, got 92
FAIL  nurture enquiry goes to follow-up, not booking
        - S3-1: expected action 'follow_up', got 'booked'
PASS  cold enquiry is archived, never booked
FAIL  full calendar escalates instead of dropping
        - expected 2 outcome(s), got 1
        - S5-2: no outcome produced
FAIL  absurd signals are clamped to the weights
        - S6-1: expected score 100, got 792
PASS  warm enquiry books too
FAIL  re-running the pipeline books nothing twice
        - expected 1 booking(s) after 2 run(s), got 2

3/8 scenarios passed
```

Read this like a professional, not like a student. Three passes include the two simplest paths, which is typical: first attempts handle the happy path. The five failures are not five random bugs. They are the Module 10 failure list wearing numbers: no deduplication, nurture treated as bookable, a dropped lead on a full calendar, unclamped extractor output, and a non-idempotent pipeline. Notice the score failure hiding inside the duplicate scenario: 92 instead of 93, the missing repeat-contact boost, visible only because the scenario asserts the exact score. Loose assertions would have called that scenario a pass on band alone.

Also notice the harness calendar is deliberately not idempotent. Booking the same enquiry twice consumes two slots there, so the re-run scenario tests whether the assistant itself owns idempotency, rather than borrowing it from a forgiving fake. Evals that forgive the exact failure they exist to catch are decoration.

## Turning the suite on your capstone

Copy `eval_harness.py` and `scenarios.json` into your project and evaluate your module:

```bash
python3 eval_harness.py assistant.agent
```

The harness accepts dicts or dataclass outcomes, so the Lesson 34 `Outcome` plugs in directly. Your acceptance bar is 8/8, and it is not negotiable downward: if a scenario seems wrong, fix the scenario only by amending the spec in your README and saying why, never by quietly weakening an expectation to make a red line green. That discipline, visibly kept, is what a technical reviewer is actually looking for in your repo.

## Hardening: from failures to a system

Evaluation tells you what breaks. Hardening is the pass that makes breakage survivable and visible:

- **Validate at the boundary.** Every external input (channel payloads, extractor output) is checked against the contract before it touches the pipeline. Clamping is the last resort; rejection with a logged reason is the first.
- **Make every write idempotent.** Bookings, follow-up scheduling, and state writes must be safe to retry, because in production everything is retried by something.
- **Log decisions, not just errors.** The event log from Lesson 34 records why each outcome happened. When (not if) a client disputes a routing decision, the log ends the argument.
- **Fail toward a human.** Overflow escalates, extractor failures route to review, nothing routes to silence. Silence is the only unacceptable failure mode in a system that handles other people's customers.
- **Add your own three scenarios.** The shipped eight are the floor. Write scenarios from your own build's near misses: the bug you almost shipped is the best test you will ever write (Lesson 25's principle, applied to yourself).

## Common failures

- **Testing the demo, not the system.** A suite that only replays the seed data proves the demo works. Adversarial cases (duplicates, overflow, absurd input, repetition) are the suite.
- **Asserting bands where scores matter.** Band-only checks pass systems whose arithmetic is quietly wrong.
- **Fixing the specimen instead of your build.** `sample_assistant.py` is a teaching specimen. Its defects are labelled in its docstring. Leave them there; the file you harden is your own.
- **A green suite you do not run.** Wire the harness into your project from this lesson onward: one command, run on every change, output quoted in your project README (next lesson).

## Recap

Outcome assertions turn "it seems to work" into eight checkable facts. The sample assistant passes three and fails five, and each failure maps to a named production failure mode from Module 10. Your capstone passes when the same suite says 8/8 against your `run()`, your hardening pass has closed the boundary, idempotency, and escalation gaps, and you have added three scenarios of your own. Next lesson: shipping it like you mean it.

## Resources

- The harness and scenarios in this lesson: `eval_harness.py`, `scenarios.json`, `sample_assistant.py`
- TechAura, QualBench (outcome regression testing for qualification and booking agents, the production-grade version of this lesson's idea): https://github.com/techaurah/qualbench
- Lesson 24 of this course, Testing agents: outcome assertions, not vibes
- Lesson 25 of this course, LLM-as-judge and human review: building an eval set from real failures
- Python json module documentation (the scenario format): https://docs.python.org/3/library/json.html
