# Exercise: a second event type, stored by type

The demo receiver understands exactly one event, `lead.created`. Real providers send families of events, and a useful receiver files them properly.

Extend the pattern from `webhook_demo.py` in a new file:

1. Accept **two** event types: `lead.created` and `booking.confirmed`.
2. Store events in a dictionary keyed by event type, so each type has its own list.
3. Reject an event whose type you do not recognise with HTTP 400, and keep rejecting bad signatures with HTTP 401, checked first as before.
4. Send three events in `main()`: two `lead.created` and one `booking.confirmed`.
5. At the end, print a summary of how many events of each type were stored.

Expected final summary:

```text
stored events by type:
  lead.created       2
  booking.confirmed  1
```

Keep everything offline, standard library only, and keep the verification-before-parsing order from the lesson. When you are done, compare with `solution/` and read why the unknown-type check sits where it does.
