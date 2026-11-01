# Exercise: recover when the first choice fails

The lesson agent lives in a kind world: the slot it wants is free. Production is not kind. In this exercise the agent's first choice is taken before it starts, and it must notice and recover.

In a new file, rebuild the lesson's loop with these changes:

1. Pre-book `friday 14:00` (`BOOKINGS = ["friday 14:00"]`) before the agent runs, simulating someone else taking the slot.
2. Keep the same two tools. Note that `book_appointment` already returns `{"ok": False, "error": ...}` for a taken slot: your job is to make the agent *use* that observation.
3. Script your fake model to prefer 14:00 anyway (models anchor on common defaults all the time), attempt it, and on observing the failure, choose the next afternoon slot, 16:30, and book that.
4. The final message must be honest about what happened: booked into 16:30, first choice already taken.
5. Keep a step limit, and keep it high enough for the longer path: the successful run now takes 4 steps.

Expected trace shape:

```text
[step 2] ACT:      book_appointment({'day': 'friday', 'time': '14:00', 'lead_id': 'LP-2026-00042'})
[step 2] OBSERVE:  {'ok': False, 'error': 'friday 14:00 is already booked'}
[step 3] ACT:      book_appointment({'day': 'friday', 'time': '16:30', 'lead_id': 'LP-2026-00042'})
[step 3] OBSERVE:  {'ok': True, 'confirmation': 'BK-1043', 'slot': 'friday 16:30', 'lead_id': 'LP-2026-00042'}
```

When it runs, read `solution/` for the design point: the loop did not change at all, and that is exactly why it is the right place for recovery to live.
