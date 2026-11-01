# Exercise 25: Teach the judge the pairing rule

Case F-009 is the uncomfortable one in this lesson's eval set: the judge failed the reply, the human failed the reply, and the agreement counter went up, but the judge failed it for the wrong reason (a missing disclaimer) and never noticed the real one (the price belonged to a different service). Verdict agreement hid a reasoning gap. Fix that, and grow the eval set the way production teams do: from new failures.

Work in copies: `my_failures.py`, `my_judge.py`, `my_run_eval.py` (update the imports in your runner to match).

1. **Give the judge the question as well as the reply.** Change the judge's interface so it receives the user message too. Add a pairing rule with a service price map (check-up $60, cleaning $90, whitening $120): when the user asks about a named service and the reply quotes a price, the quoted price must be that service's price. A mismatch is a hard fail, high confidence, with a reason that names both prices.

2. **Add two cases from the floor.** F-011: a caller asks when the clinic closes and the agent states a closing time that is wrong (the clinic closes at 5pm; invent a reply that says 8pm). Label it with the gold verdict a human would give. F-012: a caller threatens legal action and the agent stays calm, does not admit liability, and offers a callback from the practice manager. Label it too. Write honest gold reasons for both.

3. **Re-run and read the queue, not just the score.** Note what happened to F-009's reason, which new cases landed in the review queue, and whether each queueing was the system working or the system failing.

Acceptance checks:
- F-009 now fails with the pairing reason ("$90 is the cleaning price" in substance), at high confidence.
- The eval set has 12 cases and the runner reports agreement out of 12.
- F-011 lands in the review queue. If your judge somehow catches it, your gold reason must explain what extra knowledge the judge used, because the base judge has no way to know the true closing time. That gap is the point of the exercise.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
