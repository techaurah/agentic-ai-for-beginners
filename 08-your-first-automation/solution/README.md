# Solution: a fourth category, complaint, with a human handoff

Run it with `python3 solution.py`. The first three enquiries behave exactly as in the lesson; the new one ends with:

```text
enquiry from James Osei via phone transcript
  classified as: complaint
  action: HUMAN HANDOFF, no automated reply sent.
  note: queued for a person with the original message attached.

handoff queue: 1 complaint(s) waiting for a human
```

## What changed, and why

**Detection order is a safety property.** `classify()` checks complaint keywords before booking keywords, because complaint language borrows booking language ("my booking", "my appointment") constantly. In a keyword stand-in this is a line-ordering decision. In a real LLM classifier it becomes a prompt instruction with the same intent: "If the message expresses dissatisfaction with a past experience, classify as complaint, even if it mentions bookings or prices." Whichever mechanism you use, the priority must be explicit somewhere, or the most sensitive messages get the most generic handling.

**"No reply" is a designed output.** The handoff branch does not draft anything for the customer. It does two deliberate things instead: it queues the enquiry for a human, and it preserves the original message untouched, so the person picking it up reads the customer's words, not a summary of them. In production this queue is a ticket, a flagged CRM record, or a message to a staff channel, with an owner and a response-time expectation. An automation that knows when to stop is worth more than one that answers everything.

**The count at the end is an operational signal.** A handoff queue nobody counts is a queue nobody staffs. Even this tiny printout points at the real requirement: handovers need visibility, or the complaints you so carefully routed sit unread, which is worse than a mediocre automated reply.
