# Exercise: a fourth category, complaint, with a human handoff

The lesson automation answers three kinds of enquiry. The fourth kind is the one that damages businesses when an automation cheerfully mishandles it: the complaint.

Work in the Python version (`same_automation.py` pattern), in a new file:

1. Add a fourth category, `complaint`, detected **before** booking. This ordering is the heart of the exercise: "I want to complain about my booking" contains the word "booking", and a classifier that checks booking first will draft it a booking reply.
2. Add a fourth enquiry to prove it: James Osei, via "phone transcript", message: "I want to complain about my booking last week, nobody called me back."
3. Route complaints differently from everything else: **no drafted reply at all**. Instead, append the enquiry to a handoff queue and print that a human has it, with the original message preserved.
4. At the end, print how many complaints are waiting in the handoff queue.

Expected shape for the new enquiry:

```text
enquiry from James Osei via phone transcript
  classified as: complaint
  action: HUMAN HANDOFF, no automated reply sent.
```

The other three enquiries must classify and draft exactly as in the lesson. When you are done, read `solution/` for the reasoning about detection order and why "no automated reply" is itself a designed behaviour, not a missing feature. If you use n8n, sketch what the fourth branch looks like on the canvas (a second IF output, or a router before the booking check).
