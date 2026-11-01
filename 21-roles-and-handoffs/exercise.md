# Exercise: add the third role

**Time:** about 30 minutes | **Difficulty:** Intermediate

The lesson pipeline ends at a booking. Real businesses then do the thing that decides whether the customer ever books again: they follow up.

## Your task

Add a third role, `FollowUpAgent`, to `handoffs.py`:

1. Write its `RoleSpec`: mission (confirm the booking with the customer and schedule a post-visit satisfaction check), `accepts`, `produces`, and `tools`.
2. Its inputs should chain from the scheduler's `produces` (slot and booking reference) plus the minimum customer context it genuinely needs.
3. Give it a `never_receive` list. Think about what the scheduler's working data contains that a customer-facing follow-up role should never hold.
4. Implement the agent so it produces a confirmation message and a follow-up time.
5. Demonstrate both paths: a clean handoff from the scheduler that succeeds, and a "lazy integration" handoff that forwards the scheduler's entire working payload, which the contract must reject.

## What "done" looks like

- The clean chain runs end to end: intake, schedule, follow up.
- The leaky handoff is rejected, and the rejection message names the forbidden field.
- You can justify each entry on the follow-up role's `never_receive` list in one sentence.

The worked solution is in `solution/`.
