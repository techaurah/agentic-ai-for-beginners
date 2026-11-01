# Lesson 23: Multi-agent failure modes: loops, cost blowouts, conflicting outputs

**Time:** about 50 minutes | **Difficulty:** Intermediate to Advanced | **Prerequisites:** Lesson 22 (two-agent workflow), Lesson 21 (roles and handoffs)

Single agents fail in familiar ways: a wrong answer, a missed tool call. Multi-agent systems fail in ways no single agent can, because the failure lives in the interaction. This lesson simulates the three failure modes that account for most multi-agent production incidents, runs each one with the guards off so you can watch it happen, then runs it again with a small, boring guard that stops it. The guards are the lesson: none of them is clever, all of them are code, and every one of them should exist before your system meets a customer.

## Failure 1: the loop

A planner submits a draft. A reviewer applies a rule the draft can never satisfy, a sign-off line nobody told the planner about, and requests a revision. The planner, which has no way to know what is actually wrong, resubmits the same draft with fresh confidence. Forever. Neither agent is malfunctioning by its own lights; the system is.

Unguarded, the lesson's loop runs until an arbitrary platform kill at turn 50, burning 60,000 simulated tokens to produce nothing. **The guard** is a loop detector: hash each handoff's state (artifact plus last action) into a signature, count repeats, and trip when the same signature appears three times, or when a hard turn budget runs out. On trip, it does not try to fix the loop. It escalates to a human with a summary: which agents, how many turns, what never changed. Loops are design disagreements wearing a runtime costume; a human has to read the disagreement.

```
  turn 5: LOOP GUARD TRIPPED: same state seen 3 times (signature ee2de87b0f)
  ESCALATION to human: planner and reviewer disagree on a requirement neither can see.
```

## Failure 2: the cost blowout

A planner decomposes a job into subtasks. Each subtask decomposes again, or the plan simply fans out wider than anyone pictured: 16 subtasks at 1,200 tokens each is 19,200 tokens nobody approved. Decomposition feels free at planning time because the bill arrives at run time, per call, in small amounts. This is the failure mode behind most surprise agent invoices.

**The guard** is a budget cap with a running total: before each call, check whether it would breach the limit; if so, stop and return a partial result that honestly lists what was not attempted. With the cap at 10,000 tokens, the lesson's run stops after 8 of 16 subtasks and says so. A partial result with an honest gap beats a complete result with a dishonest bill, because the operator can decide whether the remaining half is worth paying for. Budgets belong in the runtime, not in a prompt that says "be economical": prompts are advice, caps are physics.

## Failure 3: conflicting outputs

Two agents answer the same customer question. One says free cancellation up to 24 hours before the visit; the other says 4 hours. Both sound fluent. Most pipelines resolve this by accident: last writer wins, or the first answer is cached, or whichever agent responded slower overwrites the other. In the unguarded run the system ships the correct answer purely because of ordering luck, and nothing in the system knows it was luck.

**The guard** is an arbiter: before an answer ships, compare it against the source of truth (here, the actual policy from Module 6's corpus). One match: ship it, flag the loser for review. No match, or a tie the truth cannot break: escalate instead of guessing. The arbiter in the lesson uses exact matching because the answers are short and factual; production arbiters range from structured field comparison to a dedicated judge model, but the shape is constant: a designated component whose only job is resolving disagreement against evidence, never by confidence.

```
  arbiter: SupportAgent CONFLICTS WITH the source of truth
  arbiter: BookingAgent MATCHES the source of truth
  shipped the BookingAgent answer, flagged the other for review
```

## What the three guards have in common

Each one is a small deterministic check wrapped around agent behaviour: a counter, a sum, a comparison. None of them uses a model. That is deliberate and it is the pattern to copy: the smarter and more probabilistic the agents, the more valuable the dumb, predictable rails around them become. Guards also share a second trait: they produce an escalation record, not just a stop. A stopped pipeline with no explanation is an outage; a stopped pipeline with "loop, turn 5, these two agents, this artifact" is a bug report.

## Why this matters in production

These are not edge cases; they are the default failure physics of systems where agents can trigger each other. Every framework will happily run your loop at full speed and full price. The teams that operate agents safely are not the ones with the best prompts; they are the ones who assumed loops, fan-outs, and disagreements on day one and built the counters before the first incident priced the lesson for them. Module 8 turns to the other half of trust: evaluating whether the system is actually any good.

## Common failures

- **Retry limits without state detection.** A cap of 50 turns is not a loop guard; it is a slower, more expensive loop. Detect repeated state, not just elapsed turns.
- **Budgets per call instead of per run.** A per-call limit does nothing against fan-out. The cap that matters is cumulative, across the whole run and all its agents.
- **Confidence-based arbitration.** Letting the more confident agent win selects for the agent that is worst calibrated. Arbitrate against evidence or escalate.
- **Silent guard trips.** The run stops, no one is told, the customer hears nothing. Every trip should write an escalation a human will actually read.
- **Guarding demos, not production.** Guards get built after the incident video, then quietly disabled when they annoy someone. A guard that can be switched off in a config file will be. Keep them in the execution path.

## Recap checklist

- [ ] I can describe the three failure modes and the interaction that causes each
- [ ] I saw each failure happen unguarded and stop guarded, with numbers
- [ ] I can explain why loop detection hashes state instead of counting turns
- [ ] I know why budgets must be cumulative per run
- [ ] I can state what an escalation record should contain

## Resources

- Anthropic engineering, "How we built our multi-agent research system" (token costs of multi-agent systems, stated plainly): https://www.anthropic.com/engineering/multi-agent-research-system
- LangGraph documentation, recursion limits and graph runtime controls: https://docs.langchain.com/oss/python/langgraph
- OpenAI Agents SDK documentation, guardrails: https://openai.github.io/openai-agents-python/guardrails/
- Microsoft AutoGen documentation, termination conditions for agent teams: https://microsoft.github.io/autogen
- CrewAI documentation, crews and task guardrails: https://docs.crewai.com

Module 7 closes here. Next, Module 8: evaluation and trust, testing agents on outcomes instead of vibes.
