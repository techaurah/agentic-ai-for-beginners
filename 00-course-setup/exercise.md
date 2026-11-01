# Lesson 00: Exercise

## Extend the checker

`check_environment.py` proves your Python is new enough and your standard library is complete. Later lessons lean on two more assumptions it never tests. Add both checks to your own copy of the script:

1. **Writable folder.** Several lessons save files (memory stores, eval reports, exports). Add a check that writes a small probe file into the current folder and deletes it again, reporting [OK] only if both operations succeed.
2. **UTF-8 text.** Agent traffic carries names, currencies, and punctuation from many languages. Add a check that encodes a string containing an accented name, a currency symbol, and a check mark to UTF-8 and decodes it back, reporting [OK] only if the round trip returns the identical string.

Both new checks must print in the same `[OK]` / `[FAIL]` format, and both must count toward the final verdict: if either fails, the script prints NOT READY and exits non-zero.

**Stretch goal:** add a third check reporting whether `git` is available on the system, as [INFO] only. Version control should never block the READY verdict.

Work in your own copy so the original stays intact for comparison. When your extended checker prints READY with four [OK] lines, compare it with the worked solution.

## Solution

See `solution/check_environment_extended.py`, with notes in `solution/SOLUTION.md`.
