# Solution: pins, the third tier

Run it:

```bash
cd 15-short-term-memory/solution
python3 solution.py
```

Output (context trimmed here):

```text
Turns kept: 6 of 9
Pins: ['Hi, my name is Amara. One important thing: I am allergic to fluoride.']
  ...
  [system] PINNED FACT: Hi, my name is Amara. One important thing: I am allergic to fluoride.

The allergy fact survives in context: True
```

## The boundary question

The exercise asked what belongs in slots, in pins, and in neither. The answer this solution implements:

- **Slots** hold task data being collected right now: service, day, customer name. They change as the task progresses, and they are read by tools.
- **Pins** hold standing facts the user states about themselves that stay true beyond this task and carry a cost if forgotten: allergies, accessibility needs, contact prohibitions. They are few by nature. If everything is pinned, nothing is.
- **Neither** holds the rest: opinions, small talk, questions already answered. That material can age out of the window safely, leaving only the trim note behind.

Two implementation details matter. Pins are deduplicated, because a user repeating an allergy in every session should not stack five copies. And pins are charged against the token budget inside `_transcript_tokens`, so a growing pin list visibly pressures the window, which is the correct incentive: pin sparingly, and promote truly permanent facts to long-term memory (Lesson 16) instead of pinning them forever.
