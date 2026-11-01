# Solution: a fourth tool, and a loop that did not change

Run it:

```bash
cd 12-function-tool-calling/solution
python3 solution.py
```

Output:

```text
USER: What is the total cost of 3 seats, in euros?
TOOL (step 1): calculator({"expression": "1250 * 3 + 99"}) -> {"result": 3849}
TOOL (step 2): convert_currency({"amount": 3849, "from_currency": "USD", "to_currency": "EUR"}) -> {"amount": 3849, "from": "USD", "to": "EUR", "converted": 3541.08}
AGENT (step 3): Summary: the package total is $3849; that is EUR 3541.08 at the teaching rate.
```

## What changed, and what deliberately did not

Three additions: the `convert_currency` function with its fixed teaching rates, one entry in the `TOOLS` registry, and one planning rule in the `FakeModel` (a request mentioning euros needs the calculator first, then the converter).

The loop, `run_agent`, is byte for byte the lesson's loop. That is the design lesson of the whole exercise: when tools are functions plus schemas in a registry, and the loop only knows how to validate, dispatch, and feed back, then new capabilities are additions, not surgery. If you found yourself editing the loop to add the tool, that is a signal the loop and the tools are tangled together.

Two details worth copying:

- The converter returns an error object for an unknown currency instead of raising, following the direction Lesson 13 develops fully.
- The rates are labelled teaching rates everywhere they appear. A learner who swaps in a live FX API later should have to change exactly one function.
