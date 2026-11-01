# Exercise 24: Catch the double booking

The suite in this lesson checks what got booked. It does not check how often the agent reached for its tools, and that gap hides a classic production bug: an agent that books the same slot twice when a caller repeats themselves (or a webhook retries). One booking is a sale. Two bookings for one caller is a very awkward phone call.

Work in copies: `my_agent.py`, `my_scenarios.py`, `my_harness.py` (the harness imports the other two, so update its imports to match your filenames).

1. **Add a tool-call budget assertion.** Extend the harness with a new assertion kind, `("tool_calls_at_most", tool_name, n)`, which fails when a tool was called more than n times in a scenario. Give it a failure message that names the tool and the actual count.

2. **Add the double-booking scenario.** The caller gives full details, books 11am, then says "Please book at 11am" again. Assert: stage is booked, the booked hour is 11, and `book_appointment` was called at most once.

3. **Fix the agent, not the test.** The careful agent from the lesson fails your new scenario: it cheerfully books twice. Change it so a repeat request for the slot it already booked is answered as a confirmation of the existing booking, with no new `book_appointment` call. Requests for a different slot are out of scope for this exercise.

Acceptance checks:
- Your harness runs 5 scenarios against the fixed agent and all pass, including the new double-booking scenario.
- The buggy agent fails the new scenario too, and fails it on the `tool_calls_at_most` assertion specifically.
- Every original scenario still passes against the fixed agent: the idempotency fix must not break the happy path.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
