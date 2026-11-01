# Lesson 10: Agent architectures compared, single agent, supervisor, pipeline, swarm

**Time:** about 45 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lesson 09 (the agent loop) · **You need:** Python 3.11 or newer. One scripted fake model powers every architecture, so runs are deterministic and free.

Lesson 09 gave you one loop. Real systems are rarely one loop: they are loops arranged into shapes, and the shape you choose decides your costs, your failure modes, and how hard the system is to debug at 2 a.m. This lesson runs the same task through three architectures and compares them honestly, including the fourth architecture, the swarm, which the demo deliberately does not build, for reasons that are themselves the lesson. By the end you will have a decision habit worth more than any single pattern: start with the simplest shape that survives your requirements, and add structure only when a named problem forces you to.

## The task and the shapes

The task is the course's running example: handle a new enquiry end to end. Classify it, check the calendar, draft a reply. One scripted fake model (the same deterministic stand-in idea as Lesson 09) sits underneath all three implementations and counts every call, so the comparison is apples to apples. Only the structure changes.

A **single agent** is one loop with all the tools. It perceives the enquiry, classifies it, checks the calendar, drafts, finishes. Maximum flexibility: because the model chooses each step, it can handle inputs nobody predicted, skip steps that do not apply, and recover from surprises the way Lesson 09's exercise showed. The cost is that every step is a model call made by a generalist, and a generalist with many tools can wander, misuse a tool, or take twelve steps to do four steps of work.

A **pipeline** is not really an agent at all: fixed stages in a fixed order, classify, then look up, then draft, with no loop and no choices. It is Lesson 08's automation wearing this lesson's vocabulary. It is the cheapest, fastest, and most predictable shape, and the easiest to test, because the path never varies. It is also brittle in a specific way: anything that does not fit the stages, a complaint, a two-part question, a booking for a service that does not exist, gets forced through them anyway, unless you build explicit exits.

A **supervisor** splits the difference. One coordinator agent plans the work and delegates each piece to a worker: a classifier worker, a drafter worker, each a small loop or call with a narrow job. In the demo, the supervisor spends one extra model call on planning, which is the pattern's signature: coordination is never free. What the extra call buys is specialisation. Each worker has a tighter prompt, fewer tools, and a smaller blast radius when it errs, and the supervisor can route around a worker that fails.

A **swarm** removes the coordinator: agents hand work to each other peer to peer, each deciding who should take the next step. It is the most flexible shape and, in current practice, the hardest to operate. Debugging a swarm means reconstructing a conversation nobody chaired. The demo does not build one because a scripted swarm would teach you the choreography and none of the pain, and the pain is the information. Treat the swarm as a specialist tool for genuinely open-ended work, not a default.

## Run it

```bash
cd 10-agent-architectures
python3 architectures.py
```

Expected output (the replies are identical by design; watch the structure and the counts):

```text
=== single agent ===
  classify -> booking
  check_calendar -> 3 free slots
  draft reply
  model calls: 2

=== pipeline ===
  stage 1 classify -> booking
  stage 2 check_calendar -> 3 free slots
  stage 3 draft reply
  model calls: 2

=== supervisor ===
  supervisor plans: classify, check calendar, draft
  delegate to classifier worker -> booking
  check_calendar tool -> 3 free slots
  delegate to drafter worker -> reply ready
  model calls: 3

=== summary ===
  single agent   model calls: 2
  pipeline       model calls: 2
  supervisor     model calls: 3
```

On a well-behaved input all three shapes produce the same reply, which is exactly the point: architecture is not about the happy path. It is about what each shape does on the day the input is weird, the calendar call fails, or the enquiry is two requests wearing a trench coat. The single agent improvises, for better and worse. The pipeline processes it wrongly, predictably, the same way every time, which at least makes the bug findable. The supervisor can notice the misfit at the planning step and route it elsewhere, if its plan step is any good, and you pay one extra call per task for that chance.

## When is each architecture wrong?

The single agent is wrong when the task is actually fixed. If ninety-five percent of your work follows the same four steps, a loop is paying model calls to rediscover a path you could have hardcoded, and accepting variance you did not need. The pipeline is wrong when inputs genuinely vary in shape, because its stages cannot skip, reorder, or ask a clarifying question. The supervisor is wrong when the work is small: below a handful of steps, coordination costs more than it saves, and a single well-tooled agent is simpler to run and to debug. The swarm is wrong as a starting point almost always, and specifically wrong wherever you owe anyone an explanation of what the system did, because peer handoffs blur accountability.

The pattern underneath all four answers: architecture follows the *variance* of your work. Low variance, pipeline. Medium variance with clear sub-jobs, supervisor. High variance in a single job, single agent. Open-ended exploration with no fixed deliverable, then, and only then, consider a swarm.

## Why this matters in production

Architecture is the decision you cannot A/B test cheaply later, because everything else, prompts, tools, traces, hiring, accumulates around the shape. The demo's small numbers scale brutally: one extra coordination call per task is nothing at a hundred tasks a day and a serious line item at a million, and the failure you will actually meet is never the one in the brochure. It is the supervisor confidently delegating a complaint to the booking worker, or the pipeline drafting a lovely reply to a message that was a legal threat. Choosing the simplest shape that fits, and knowing precisely which named problem would make you upgrade it, is what senior agent engineering mostly consists of. Module 7 returns to these shapes with real frameworks and real handoffs.

## Common failures

- **Starting with the impressive shape.** Multi-agent demos photograph well. Production bills and debugging sessions do not care. Earn complexity; never borrow it.
- **Giving every worker every tool.** Specialisation only pays when workers are actually narrow. A supervisor delegating to three generalists is a single agent with extra calls.
- **No owner of the final answer.** In supervisor and swarm designs, name the component accountable for the output a human sees, or failures become everybody's secondhand problem.
- **Comparing architectures on happy inputs.** They tie. Compare them on failures, weird inputs, and cost per completed task, or you have compared nothing.
- **Treating the pipeline as a failed agent.** It is often the right answer. Lesson 08's automation will out-earn most agent demos precisely because it never improvises.

## Recap checklist

- [ ] I can describe all four shapes and the coordination cost of each.
- [ ] I ran the demo and can explain why the supervisor costs one more call.
- [ ] I can state a task where each architecture is the wrong choice.
- [ ] I know the rule: architecture follows the variance of the work.
- [ ] I can name the component that owns the final answer in each shape.

## Resources

- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents), workflows versus agents, and the pattern catalogue this lesson compresses.
- [LangGraph: multi-agent systems documentation](https://langchain-ai.github.io/langgraph/concepts/multi_agent/), supervisor, network (swarm), and hierarchical shapes from a framework that ships them.
- [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/), single versus multi-agent trade-offs, framed for product teams.
- [Microsoft: AI agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns), sequential, concurrent, group chat, and handoff patterns as architecture guidance.
