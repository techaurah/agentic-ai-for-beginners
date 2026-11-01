# Solution 24: Catch the double booking

Three files changed, one per part of the exercise.

**The budget assertion (`harness.py`).** `tool_calls_at_most` counts occurrences of the tool name in the transcript's tool call list and compares against the budget. The failure message names the tool, the actual count, and the budget, because a failing test you have to debug is a tax on every future run.

**The scenario (`scenarios.py`).** `double-booking` replays a pattern every real system meets: a caller (or a retrying webhook) asks for the same slot twice. It asserts the outcome (booked, hour 11, phone captured) plus the new budget: `book_appointment` at most once.

**The agent fix (`agent.py`).** The repeat request is intercepted before any tool call: if this agent already holds a booking at the requested hour, the reply confirms the existing booking and returns. The guard sits in the careful variant only, and it keys on state (stage plus booked hour), not on the caller's wording, so "book at 11am", "book 11am again", and a silent webhook retry all land in the same place.

Verified behaviour: the fixed agent passes all 5 scenarios (23 assertions). The buggy agent fails the new scenario on exactly the assertion the exercise named, `tool_calls_at_most: tool 'book_appointment' was called 2 times, budget is 1`, alongside its phone-capture defect.

The generalisable point: idempotency is an outcome property, so it belongs in the outcome suite. Any agent action that writes to the world (book, send, charge, create) deserves a budget assertion and a repeat-the-request scenario. Retries are not an edge case; they are how distributed systems normally behave.
