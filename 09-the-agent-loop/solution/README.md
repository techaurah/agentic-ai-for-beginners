# Solution: recover when the first choice fails

Run it with `python3 solution.py`. The decisive steps:

```text
[step 2] ACT:      book_appointment({'day': 'friday', 'time': '14:00', 'lead_id': 'LP-2026-00042'})
[step 2] OBSERVE:  {'ok': False, 'error': 'friday 14:00 is already booked'}

[step 3] DECIDE:   14:00 failed: already booked. The observation told me the truth my plan lacked. Next afternoon option is 16:30.
[step 3] ACT:      book_appointment({'day': 'friday', 'time': '16:30', 'lead_id': 'LP-2026-00042'})
[step 3] OBSERVE:  {'ok': True, 'confirmation': 'BK-1043', 'slot': 'friday 16:30', 'lead_id': 'LP-2026-00042'}

[step 4] FINISH:   Booked LP-2026-00042 into friday 16:30 (confirmation BK-1043). First choice 14:00 was already taken.
```

## What changed, and why

**Only the model script changed. The loop, the tools, and the limit did not.** That is the payoff of the Lesson 09 architecture: recovery is a decision problem, not a plumbing problem. The failed booking came back as an ordinary observation, the next decide step reasoned over it, and the loop carried on. If your agent design needs new machinery every time the world says no, the design, not the world, is the problem.

**The failure had to be visible to be useful.** This works because `book_appointment` returns an explicit `{"ok": False, "error": ...}` instead of raising, pretending, or returning an empty success. The error text even names the slot, which is what lets the next decision be specific ("next afternoon option") rather than a blind retry of the same call.

**The final message reports the detour.** It would have been easy to announce "Booked into friday 16:30" and omit the failed attempt. In production that omission becomes a support ticket when the customer says "but I asked for 14:00". Agents that narrate their own recoveries are agents people can trust with bookings.
