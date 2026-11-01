# Lesson 01: Solution notes

Run it:

```bash
python3 agent_with_reschedule.py
```

Expected output: turns 1 and 2 identical to the lesson, then turn 3 where the chatbot promises a team member will follow up (and changes nothing), while the agent cancels BK-1001, books BK-1002 at 12:30, and the summary shows one active booking and one cancelled.

**What changed and why.** Three additions. `cancel_booking` joins the tool set, because rescheduling is two world changes, not one. Bookings gain a `status` field, because a cancelled booking must remain visible in the record; deleting it would erase the audit trail production systems depend on. And the reschedule rule is checked *before* the booking rule in `handle`, because the message contains a time and could otherwise be mistaken for a fresh booking, leaving the customer with two appointments.

**What to notice.** The chatbot is not lying maliciously; it has no state to lie about. It cannot know a booking exists, so it cannot know one needs moving. That is the structural point of the lesson: capabilities follow architecture, not tone of voice.
