# Exercise: facts that expire, and a way to delete everything

The lesson's store remembers forever until a single key is forgotten. Real stores need two more behaviours:

**Part 1: expiry.** A preference learned two years ago may simply be stale. Add a time-to-live to every fact:

1. `remember()` accepts `ttl_days` with a sensible default (the solution uses 180).
2. `recall()` takes the current day and returns `None` for an expired fact, exactly as if it had never been stored. Callers should not need to know the difference between "never known" and "expired".
3. Add `sweep_expired(today)` that removes expired facts from the file and returns the keys it removed.

**Part 2: forget everything.** "Delete everything you remember about me" is a single request a customer can make, and it should take a single call:

4. Add `forget_all()` that empties the store, saves the empty state, and returns how many facts were removed.

**Done when:** your demo stores a normal fact and a short-lived fact (7-day TTL) on day 1; on day 30 the short-lived fact recalls as `None`, the sweep reports it removed, the normal fact still recalls, and after `forget_all()` a recall returns `None` and the reported count matches what was left.

The worked solution is in `solution/`. Read its note on why expired facts are treated as gone at recall time, not only when the sweep runs.
