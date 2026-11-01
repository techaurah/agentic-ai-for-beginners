# Solution: a second event type, stored by type

Run it with `python3 solution.py`. Output:

```text
receiver: listening on http://127.0.0.1:8765/webhooks/events
receiver: stored 'lead.created' (HTTP 200)
receiver: stored 'lead.created' (HTTP 200)
receiver: stored 'booking.confirmed' (HTTP 200)
stored events by type:
  lead.created       2
  booking.confirmed  1
```

## What changed, and why

**The store became a dictionary of lists.** `store = {"lead.created": [], "booking.confirmed": []}` replaces the single flat list. Filing by type is what lets a real receiver route work: a new lead goes to the qualification flow, a confirmed booking goes to the reminder flow, and neither has to know about the other.

**The order of checks is deliberate: signature, then type, then store.** The 401 check still runs before the body is parsed. The type check runs after parsing (you cannot know the type without reading the JSON) but before storing, so an unknown type is rejected with a 400 and never lands in state. A 400 also tells the provider "your request is wrong", which stops most providers retrying, while a 401 tells it "your identity is wrong". Using the right status code is part of the API contract.

**Unknown types are rejected, not ignored.** A quieter design would store anything and sort it out later. Rejecting is safer for agents: an event type you do not recognise is often a provider-side change you need to hear about loudly, not discover weeks later in a bloated store.
