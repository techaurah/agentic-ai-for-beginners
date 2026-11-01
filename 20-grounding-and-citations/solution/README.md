# Solution: contradiction detection (rule R4)

Run it:

```bash
python3 solution.py
```

Output:

```
R4 FLAGS (1):
  ! claim 2: cited span S10 is NEGATED but the claim is positive (shared words: cover, manchester) -> review (rule R4)
```

## How the rule works

`check_contradictions` skips claims that are themselves negated (a claim that keeps the "do not" is faithful, not flipped). For the rest, it checks whether any cited span contains negation wording while sharing at least two key words with the claim. Two shared words is the tripwire: one shared word is usually a topic match, two usually means the claim is talking about the same fact the span negates.

## Why it flags instead of failing

Negation is slippery. "We do not require a deposit" cited by the claim "No deposit is needed" is a correct paraphrase that a naive rule would flag, and "not only repairs but also installations" contains "not" without negating anything. A hard fail on this signal would train operators to ignore the checker. A review flag puts a human on exactly the claims where meaning can invert, which is a small, affordable set. Knowing which of your checks are verdicts and which are suspicions is part of designing verification honestly.
