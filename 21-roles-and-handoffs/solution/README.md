# Solution: the FollowUpAgent role

Run it:

```bash
python3 solution.py
```

Output (trimmed):

```
HANDOFF SchedulingAgent -> FollowUpAgent: fields ['booking_reference', 'customer_name', 'proposed_slot']
  ok contract satisfied
FOLLOW-UP produced: {'confirmation_message': 'Hello Mrs Carter, your visit is confirmed for tomorrow 09:00 (ref NB-1042). ...', 'follow_up_time': 'visit + 24h'}

HANDOFF SchedulingAgent -> FollowUpAgent: fields ['booking_reference', 'customer_name', 'internal_notes', 'proposed_slot']
  x REJECTED: forbidden field for FollowUpAgent: internal_notes
```

## Design choices worth noticing

The follow-up contract accepts exactly three fields: name, slot, reference. It does not accept the job summary or urgency, because confirming a booking does not need them; if a future feature does, the contract changes deliberately, in code, where a reviewer can see it.

The interesting entry is `internal_notes` on the `never_receive` list. The scheduler's notes ("customer sounded stressed; price sensitive") are operationally useful and commercially sensitive. A customer-facing agent holding them is one prompt injection or one logging mishap away from quoting them to the customer. The contract makes that accident structurally impossible rather than merely discouraged.

That is the habit this lesson is really teaching: every field in a handoff should have to argue for its place.
