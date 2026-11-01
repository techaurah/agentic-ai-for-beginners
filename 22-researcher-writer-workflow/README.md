# Lesson 22: Building a two-agent workflow: researcher plus writer

**Time:** about 60 minutes | **Difficulty:** Intermediate to Advanced | **Prerequisites:** Lesson 21 (roles and handoffs), Lesson 11 (planning and reasoning patterns)

Lesson 21 gave two agents a contract. This lesson gives them a structure: an explicit graph where a Researcher gathers findings, a Writer drafts a brief from them, and a Reviewer can send the draft back. You will build the whole thing on a small graph engine written in pure Python, deliberately, and then map every piece onto LangGraph, the framework this structure comes from. Reading a 90-line engine you fully understand beats importing a framework you half understand, the first time.

> A note on naming: the code in this lesson is a **LangGraph-style teaching model**. It is not LangGraph, and it does not pretend to be. It reproduces LangGraph's core ideas (shared state, nodes, edges, conditional edges) with the machinery exposed, so that when you open the real framework, you recognise everything.

## The shape of the workflow

```
researcher ──> writer ──> reviewer ──┬── accept ──> END
                                     └── rewrite ──> writer (once)
```

Three design decisions do the heavy lifting:

1. **Shared state, partial updates.** There is one state dictionary (topic, findings, brief, verdict, retries). Each node reads what it needs and returns only the keys it changes. Nodes never call each other; the graph routes. This is what makes nodes replaceable: swap the Researcher's keyword search for a real retriever (Lesson 19) and the Writer never notices.
2. **The review is a node, not a hope.** Quality control is a step in the graph with a verdict in state, not a paragraph in the Writer's prompt asking it to "please be accurate".
3. **The loop is conditional and capped.** The edge from reviewer back to writer fires only on a "rewrite" verdict, and the reviewer itself stops demanding rewrites after one round. Every cycle in a graph needs both a condition and a budget; Lesson 23 shows what happens without them.

## Walking through the run

```bash
python3 researcher_writer_graph.py
```

```
  NODE researcher: {'findings': '<3 items>'}
  NODE writer: {'brief': 'Brief: why small plumbing firms lose bookings...'}
  NODE reviewer: {'verdict': 'rewrite', 'review_notes': 'include findings from: Pricing transparency n...', 'retries': 1}
  NODE writer: {'brief': 'Brief: why small plumbing firms lose bookings...'}
  NODE reviewer: {'verdict': 'accept', 'review_notes': ''}
```

What happened: the Researcher scored a small source corpus against the topic and kept the three best findings. The Writer's default style keeps briefs to the two strongest findings, so the first draft dropped the pricing finding. The Reviewer checked a mechanical rule, every finding's title must appear in the brief, found one missing, and routed back with a specific note. The Writer, seeing review notes, switched to completeness over brevity. The Reviewer accepted. Notice the feedback was a field in state, not a chat message: Lesson 21's contract discipline, applied inside a graph.

## How does this map to real LangGraph?

Almost one to one:

| Teaching model (this lesson) | LangGraph |
|---|---|
| `state` dict passed to every node | Typed state (a `TypedDict` or Pydantic model) with reducers |
| `add_node(name, fn)` | `builder.add_node(name, fn)` |
| `add_edge(a, b)` | `builder.add_edge(a, b)` |
| `add_conditional_edge(a, router)` | `builder.add_conditional_edges(a, router)` |
| `Graph.run(state)` | `graph = builder.compile(); graph.invoke(state)` |
| `max_steps` guard in `run` | `recursion_limit` in the invoke config |

What the real framework adds, and the teaching model leaves out on purpose: persistence and checkpointing (state saved at every step, so a long workflow can pause, resume, and time-travel), streaming of intermediate results, human-in-the-loop interrupts at any node, and parallel branches with proper state reducers. When your workflow needs any of those, graduate to LangGraph and bring the structure with you. The nodes you wrote here port almost unchanged, because they were never coupled to the engine: they read state and return updates.

## Why a graph, and not just agent A calling agent B?

Because the interesting behaviour is in the routing, and routing hidden inside prompts cannot be inspected, tested, or capped. In the graph, the rewrite loop is one visible edge with one visible condition. You can unit-test the Reviewer alone, log every transition, and answer the production question from Lesson 21: what exactly happened, in what order, with what state. Chains of agent calls work for demos; graphs are what you debug at 2 a.m.

## Common failures

- **State as a junk drawer.** Every node dumps everything into state, names collide, and no one knows which keys are load-bearing. Declare your state keys up front, as this lesson does informally and LangGraph does with types.
- **Reviewers that only praise.** A review node whose prompt says "check quality" with no mechanical criteria accepts everything. Give reviewers checkable rules first (all findings used, all claims cited, length within bounds) and judgement second.
- **Unbounded cycles.** A rewrite edge with no retry budget is a loop waiting for a stubborn pair of agents. Cap retries in state, and make the cap reachable.
- **Writers that re-research.** When the Writer quietly does its own searching, your findings, sources, and costs split across two nodes and the Reviewer can no longer verify provenance. One job per node.
- **Skipping the trace.** If the graph does not log its transitions, multi-agent debugging becomes reading final output and guessing. The lesson's `run` prints every node and its update for a reason.

## Recap checklist

- [ ] I can draw the researcher, writer, reviewer graph from memory
- [ ] I can explain partial state updates and why nodes return only what they change
- [ ] I saw a conditional edge fire once, and know what stopped it firing forever
- [ ] I can map the teaching engine's pieces onto LangGraph's API
- [ ] I know two things real LangGraph adds (checkpointing, interrupts) and when I would need them

## Resources

- LangGraph documentation: https://docs.langchain.com/oss/python/langgraph
- LangGraph conceptual overview, graphs and state: https://docs.langchain.com/oss/python/langgraph/overview
- LangChain Academy (LangGraph course repo, the workbook pattern this course also follows): https://github.com/langchain-ai/langchain-academy
- Anthropic engineering, "How we built our multi-agent research system" (a production researcher plus workers architecture): https://www.anthropic.com/engineering/multi-agent-research-system
- OpenAI Agents SDK documentation, handoffs and guardrails: https://openai.github.io/openai-agents-python/

Next: Lesson 23 breaks this kind of system on purpose: loops, cost blowouts, and conflicting outputs, and builds the guards for each.
