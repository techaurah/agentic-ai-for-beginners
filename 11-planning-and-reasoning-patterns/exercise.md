# Exercise: ReAct when a tool cannot answer

The lesson's ReAct agent lives in a world where every lookup succeeds. Real price lists have gaps, and the most damaging thing an agent can do with a gap is fill it with an invented number.

Extend the ReAct pattern in a new file:

1. Ask a two-part question with a trap in it: "What does a root canal cost, and are you open Saturday?"
2. Keep the lesson's tools. `price_lookup` already answers honestly for missing services: `root canal: not in the price list`. Your job is the agent's behaviour around that observation.
3. Script the trace so the agent: tries the price lookup, **reads the miss and explicitly refuses to guess**, still answers the calendar half of the question, and finishes with a final answer that separates what it knows (Saturday 10:00 is free) from what it does not (the root canal price), promising a human will confirm the price.
4. Add a handoff note line at the end recording the missing price, the way Lesson 08's complaint exercise queued work for a person.

Expected shape:

```text
question: What does a root canal cost, and are you open Saturday?
  Action:      price_lookup({'service': 'root canal'})
  Observation: root canal: not in the price list
  ...
  Handoff note:  root canal pricing requested, not in price list.
```

The rule your implementation must honour: **no price may appear in the final answer that did not come from the tool.** When it runs, read `solution/` on why this behaviour is a design choice you make in the pattern, not a property you can prompt for and hope.
