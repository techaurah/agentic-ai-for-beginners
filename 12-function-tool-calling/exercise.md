# Exercise: add a fourth tool to the loop

The lesson's agent can calculate, check a calendar, and score a lead. A client just asked the question agents get every day: "Fine, but what is that in euros?"

Add a `convert_currency` tool to `tool_calling_loop.py`:

1. Write a `convert_currency(amount, from_currency, to_currency)` function. Use a small dictionary of fixed teaching rates (for example USD 1.0, EUR 0.92, GBP 0.79, AED 3.67). It must not call any network API.
2. Register it in `TOOLS` with a description and a parameter schema, following the pattern of the existing three tools.
3. Teach the `FakeModel` to use it: when the user request mentions euros or EUR, the model should first get the USD total from `calculator`, then convert that result. The conversion amount must come from the calculator's result, not from a hardcoded number in the model.
4. Add a scenario to the demo: "What is the total cost of 3 seats, in euros?" and run it.

**Done when:** your run shows the calculator and the converter called in sequence, and the final answer quotes the converted amount. If the model asks for the conversion before the total exists, your plan ordering is wrong, and the transcript will show it.

Stuck? The worked solution is in `solution/`, with an explanation of the one design point that matters: why adding a tool required no changes to the loop itself.
