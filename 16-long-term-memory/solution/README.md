# Solution: expiry at recall time, not just sweep time

Run it:

```bash
cd 16-long-term-memory/solution
python3 solution.py
```

Output:

```text
Day 5:  preferred_time -> {'value': 'morning', 'source': 'session-1', 'day': 1, 'ttl_days': 180}
Day 5:  short-lived fact -> {'value': 'prefers a text before visits', 'source': 'session-1', 'day': 1, 'ttl_days': 7}
Day 30: short-lived fact -> None (expired: treated as gone)
Day 30 sweep removes: ['gate_code_note']
Day 30: preferred_time -> {'value': 'morning', 'source': 'session-1', 'day': 1, 'ttl_days': 180}

Customer: 'Delete everything you remember about me.'
forget_all removed 1 fact(s)
Recall after wipe: None
```

## Two design points

**Expiry is enforced in `recall()`, not only in the sweep.** A sweep runs when someone remembers to run it: nightly, weekly, on startup. Between sweeps, an expired fact sitting in the file would still be returned to any caller who asks. Checking the TTL at recall time makes expiry a property of the store, not of the housekeeping schedule. The sweep then exists purely to reclaim space and to give you a report of what died.

**Defaults carry the policy.** The 180-day default TTL means a fact learned by accident of omission still ages out; facts that genuinely deserve permanence can be stored with a longer TTL explicitly, which makes permanence a decision instead of an accident. `forget_all()` returning a count is the same instinct: the customer hears "we deleted N facts about you", a number they can sanity-check, rather than a bare "done".
