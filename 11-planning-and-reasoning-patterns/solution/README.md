# Solution: ReAct when a tool cannot answer

Run it with `python3 solution.py`. Output:

```text
question: What does a root canal cost, and are you open Saturday?
  Thought:     The question has two parts: a root canal price and Saturday hours. Price first.
  Action:      price_lookup({'service': 'root canal'})
  Observation: root canal: not in the price list
  Thought:     The price list has no root canal entry. I will NOT guess a number. I can still answer the calendar half, then flag the price for a human.
  Action:      calendar_lookup({'day': 'saturday'})
  Observation: saturday: free slots ['10:00']
  Final answer: I cannot quote a root canal price from our list,
                so I will not invent one: a member of the team will
                confirm it. Saturday does have a free slot at 10:00
                if you would like us to hold it meanwhile.
  Handoff note:  root canal pricing requested, not in price list.
```

## What changed, and why

**The observation was allowed to veto the plan.** The question invited a two-lookup answer. When the first lookup returned a miss, the trace did not smooth it over; the next thought names the miss and redesigns the answer around it. This is ReAct's core strength used deliberately: every observation is a chance to change course, including the course of admitting a gap.

**"I do not know" was composed, not fallen into.** The final answer does three jobs at once: it states the limit plainly, it salvages the half of the question that could be answered (Saturday at 10:00), and it converts the gap into a commitment (a person will confirm the price) plus a handoff note, so the gap lands on a human's list instead of evaporating. In a real system the equivalent moves are an instruction in the prompt ("never state a price that did not come from the price tool"), a validator that rejects drafts quoting numbers absent from tool outputs, and a handoff queue like Lesson 08's. Layers, not hope.

**Partial answers beat blocked answers.** A weaker design would refuse the whole question because one part failed. Customers asked two things; answering one well and escalating the other honestly is both better service and better business. Agents that can degrade gracefully are the ones that survive contact with real data, which is always, always incomplete.
