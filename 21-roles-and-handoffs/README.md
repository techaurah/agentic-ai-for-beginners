# Lesson 21: When one agent is not enough: roles and handoffs

**Time:** about 45 minutes | **Difficulty:** Intermediate | **Prerequisites:** Lesson 10 (agent architectures compared), Lesson 13 (designing tools)

One agent with twenty tools and a giant prompt is not a system; it is a bottleneck with good marketing. Real work splits naturally: someone talks to the customer, someone else books the visit, someone else follows up. Multi-agent design starts the moment you split that work, and most of its failures happen not inside the agents but between them, at the handoff. This lesson is about designing the handoff as a contract before you write a single agent prompt.

## What is a role, exactly?

A role is a bounded responsibility with four edges, and `handoffs.py` writes them down as a `RoleSpec`:

- **Mission.** One sentence: what this role exists to do. If you cannot write it in one sentence, the role is two roles.
- **Accepts.** The fields a handoff to this role must contain. Not "context", not "whatever the last agent had": named fields.
- **Produces.** The fields this role guarantees to output, which become the next role's possible inputs. Contracts chain: one role's `produces` list is the next role's menu.
- **Tools.** The only tools this role may call. A scheduling agent that can also send marketing emails will eventually do so at the wrong moment.

There is a fifth edge, the one beginners skip: **never_receive**. The scheduling agent in this lesson never receives card numbers or passwords, not because it would misuse them on purpose, but because data a role never holds can never leak through it, get logged by it, or be repeated by it. Least privilege is a prompt-injection defence as much as a privacy rule: the smaller the payload, the smaller the blast radius when any part of the chain is manipulated.

## What happens at a handoff?

The lesson's pipeline is deliberately small. An `IntakeAgent` reads a customer message and produces a structured enquiry. Before the `SchedulingAgent` sees it, `validate_handoff` checks the payload against the scheduler's contract: all required fields present and non-empty, no forbidden fields attached. Only then does the receiving agent run.

The second handoff in the demo is the lesson:

```
HANDOFF IntakeAgent -> SchedulingAgent
  payload fields: ['card_number', 'customer_name', 'job_type', 'summary']
  x REJECTED: missing required field: urgency
  x REJECTED: forbidden field for SchedulingAgent: card_number (least privilege: this role never needs it)

Pipeline stopped safely: SchedulingAgent refused the handoff
```

That payload is what real integrations produce: a rushed form handler forwarding everything it captured, minus the one field the next step actually needed. Without a contract, the scheduler would have run anyway, guessed the urgency, and held a card number it had no business touching. With a contract, the pipeline stops loudly at the seam, where the bug is cheap.

## Why not just pass the whole conversation?

Because "the whole conversation" is how context windows fill with noise, costs multiply at every step, and agents inherit each other's mistakes as facts. A contract payload is smaller, testable, and reviewable. It also gives you something priceless in production: a seam you can log. When a multi-agent system misbehaves, the first diagnostic question is "what exactly crossed each handoff?" If you cannot answer that from logs, you do not have a system, you have a séance.

None of this requires a framework. Frameworks (Lesson 22 looks at LangGraph) provide state and routing plumbing. The contract is a design decision that sits above any framework, and it survives framework changes, which is more than can be said for most agent code.

## When should you split into roles at all?

Split when at least one of these is true: the steps need different tools or permissions; the steps need different models (a cheap classifier feeding an expensive reasoner); a human must approve between steps; or one step's failures must not contaminate another's context. Stay with one agent when the task is a single short loop with one toolset. Every role you add buys specialisation and pays for it in handoffs, and handoffs are where your engineering hours will go.

## Common failures

- **The telephone game.** Each agent summarises the last one's output in its own words, and by agent four the customer's actual words are gone. Contracts fix this: facts travel as fields, not as retellings.
- **God payloads.** Passing every field "just in case" defeats least privilege and bloats every prompt downstream. Accept lists should be short enough to argue about.
- **Implicit contracts.** The two agents were prompted by the same person on the same day, so the formats match, until someone edits one prompt. Write the contract in code and validate it; prompts drift, validators do not.
- **No refusal path.** A receiving agent that cannot reject a bad handoff will process it badly. Refusal is a feature: build the error message so the upstream side knows exactly what to fix.
- **Role sprawl.** Twelve narrow agents where three would do. Each seam is a failure surface, a latency cost, and a debugging burden.

## Recap checklist

- [ ] I can state the four edges of a role, plus never_receive
- [ ] I can explain why facts should travel as fields, not summaries
- [ ] I saw a handoff get rejected for both a missing field and a forbidden field
- [ ] I know three honest reasons to split work into roles
- [ ] I understand why the contract lives in code, not in prompts

## Resources

- Anthropic, "Building effective agents" (on when multi-agent and workflow patterns earn their complexity): https://www.anthropic.com/research/building-effective-agents
- Anthropic engineering, "How we built our multi-agent research system" (handoff and coordination lessons from production): https://www.anthropic.com/engineering/multi-agent-research-system
- OpenAI, "A practical guide to building agents" (manager and handoff patterns): https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- LangGraph documentation, multi-agent concepts: https://docs.langchain.com/oss/python/langgraph
- OWASP, LLM prompt injection guidance (why least-privilege payloads matter): https://owasp.org/www-project-top-10-for-large-language-model-applications/

Next: Lesson 22 builds two roles into a real workflow with explicit state, a researcher and a writer, using a graph structure.
