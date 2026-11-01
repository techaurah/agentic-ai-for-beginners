# Solution: the FactCheck node

Run it:

```bash
python3 solution.py
```

Output (trimmed):

```
Pass 2: writer invents a statistic (tamper on)
  NODE writer
  NODE fact_check
    -> fact_check: fail (claim cites UK boiler market note but is not supported by it)
  NODE writer
  NODE fact_check
    -> fact_check: pass
```

## How it works

`fact_check` parses each bullet into claim plus cited title, looks the title up in the findings, and applies the Lesson 20 support rule: at least half the claim's content words must appear in the cited finding. The invented claim ("answer within 5 minutes win 90 percent of bookings") shares almost nothing with the real finding beyond "within", so it fails at roughly 8 percent support. The conditional edge routes back to the writer with the failure named; the rewrite drops the invented claim; the second check passes.

## Why a separate node, not a bigger reviewer

Separation keeps each checker honest and testable. The reviewer judges coverage (were the findings used); the fact checker judges support (are claims anchored). They fail differently, get fixed differently, and in a bigger system they are owned by different logic entirely: support checking is the Lesson 20 grounding machinery, reused. When one node does five kinds of checking, its failures tell you nothing about which kind went wrong, and you are back to reading output and guessing.
