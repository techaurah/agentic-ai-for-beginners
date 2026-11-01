# Lesson 24: Testing Agents: Outcome Assertions, Not Vibes

**Time:** 45-60 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 09 (the agent loop), 13 (designing tools)

## The hook

Every agent demo works. The agent books the appointment, answers the question, charms the room. Then it ships, and on a wet Tuesday it books a patient into a slot that was already taken, at 7pm, without ever asking for a phone number. Nothing crashed. No error was thrown. The agent simply did the wrong thing, fluently, and nobody noticed until a human did.

This lesson is about noticing before your customers do. You will build a small test harness that judges an agent the way a business judges it: not by how the replies read, but by what actually happened.

## Why can't you just read the replies?

Because fluent text hides broken outcomes. An agent can write "You are all booked in!" while booking nothing, or book the wrong hour while apologising beautifully. Reading output is a vibe check. It does not scale past a handful of conversations, it cannot run in CI (continuous integration, the practice of running your tests automatically on every change), and two reviewers will disagree about whether a reply "seems fine".

The alternative is an **outcome assertion**: a check against the state of the world after the agent acted. Did a booking exist at the end? At which hour? Was the phone number captured? Which tools were called, and how many times? State is either right or wrong, and a machine can check it at 3am without an opinion.

## What does a scenario look like?

A scenario has three parts: a script of user turns, the agent run against them, and a list of assertions about the resulting transcript. The transcript here means everything observable: final stage, captured fields, tool calls, and the replies (checked mechanically, for required or forbidden phrases, never for style).

This lesson's agent is a small deterministic front desk for Brightpath Dental, the fictional clinic used across this module. It takes bookings between 9am and 5pm, refuses taken slots, and must capture a phone number before confirming. There are two variants. The careful one follows the rules. The buggy one ships with four realistic defects: it skips the hours check, skips the taken-slot check, loses the phone number, and uses the word "guarantee", which the clinic never allows.

## Worked example

Run the harness:

```bash
python3 harness.py
```

The suite runs the same four scenarios against both agents. The careful agent passes everything:

```text
Suite: careful agent (must pass everything)
  [PASS] happy-path: Books a free slot when the caller gives full details (9 assertions)
  [PASS] taken-slot: Refuses a slot that is already booked and offers another (4 assertions)
  [PASS] after-hours: Refuses a booking outside business hours (3 assertions)
  [PASS] missing-phone: Does not confirm a booking without a phone number (3 assertions)
  Result: 4/4 scenarios passed, 0 assertions failed
```

The buggy agent fails all four scenarios, and the failures read like an incident report:

```text
Suite: buggy agent (must not pass)
  [FAIL] taken-slot: Refuses a slot that is already booked and offers another
         - no_booking: expected no booking, but hour 10 was booked
         - booked_hour_is_not: booked hour 10 must never be booked
         - reply_contains: no reply contains 'taken'
  [FAIL] after-hours: Refuses a booking outside business hours
         - no_booking: expected no booking, but hour 19 was booked
  Result: 0/4 scenarios passed, 12 assertions failed
```

Read the files in this order. `agent.py` is the system under test, kept deliberately plain so the testing idea stays in front. `scenarios.py` is data, not code: each scenario is a dictionary of turns and assertion tuples, so adding a test means adding a dictionary, not a framework. `harness.py` runs a scenario against a fresh agent, builds the transcript, and evaluates each assertion with a failure message that says what the world looked like instead. That last part matters. "Assertion failed" is useless at 3am; "expected no booking, but hour 10 was booked" is a diagnosis.

Notice the design choice in the demo: the buggy suite is expected to fail, and the harness treats "the careful agent passes and the buggy agent gets caught" as the success condition. A test suite that has never caught anything is not evidence your agent is good. It is evidence your tests are weak. Keeping a known-bad agent around as a sparring partner is how you prove the suite still has teeth after every refactor.

This approach is the teaching core of [QualBench](https://github.com/techaurah/qualbench), TechAura's open-source agent evaluation tool: scenario packs, outcome assertions over transcripts, and pass/fail you can defend in a review meeting. This lesson is the hand-built miniature. QualBench is the same idea grown up, with more assertion types and scenario packs for lead qualification.

## Why this matters in production

Agents change underneath you. The model gets updated, the prompt gets edited, a tool's behaviour drifts. Without an outcome suite, every change is a leap of faith followed by a support ticket. With one, a change is a pull request and a number: scenarios passed before, scenarios passed after. The suite also becomes your regression memory. Every production incident from Lesson 25 onward should end as a new scenario, so the same failure can never ship twice silently.

## Common failures

- **Asserting on wording.** Checking that a reply "sounds apologetic" breaks every time the model rephrases. Assert on state, tool calls, and a small list of required or forbidden phrases only.
- **One giant scenario.** A 30-turn script that fails tells you nothing about where. Small scenarios with names are debuggable; sagas are not.
- **Testing only the happy path.** The valuable scenarios are the refusals: taken slot, after hours, missing details. Correct refusal is half of an agent's job.
- **A suite that never fails.** If months pass without a red run, suspect the tests, not the agent. Feed it a deliberately broken variant, like this lesson does.

## Recap

- [ ] Judge agents by outcomes (state, fields, tool calls), not by how replies read
- [ ] A scenario is scripted turns plus assertions over the transcript
- [ ] Failure messages should describe the world, not just say "failed"
- [ ] Keep a known-buggy variant to prove the suite can still catch defects
- [ ] Every production incident becomes a new scenario

## Resources

- [QualBench: outcome-based agent evaluation (the teaching tool behind this lesson)](https://github.com/techaurah/qualbench)
- [Python `unittest` documentation](https://docs.python.org/id/3.14/library/unittest.html): the standard library framework, for when your harness outgrows a script
- [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): designing evals that measure what you actually care about
- [OpenAI: Working with evals](https://developers.openai.com/api/docs/guides/evals): the same discipline applied through a hosted evals API
