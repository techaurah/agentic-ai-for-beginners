# Lesson 11: Planning and reasoning patterns, ReAct, plan-and-execute, reflection

**Time:** about 45 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 09 and 10 (the loop, and the shapes it takes) · **You need:** Python 3.11 or newer. All three patterns run on one scripted fake model: deterministic, offline, free.

The loop from Lesson 09 answers one question: what happens mechanically, step by step. This lesson answers the next one: how should the agent *think* across those steps? A reasoning pattern is a discipline for the decide step. It shapes what the model considers, in what order, and what it is allowed to conclude from. Three patterns cover most of what you will meet in real systems and in every framework's documentation: **ReAct**, which interleaves reasoning with action; **plan-and-execute**, which separates the plan from the doing; and **reflection**, which makes the agent grade its own work before anyone else sees it. Each has a home ground and a failure mode, and the demo runs all three against the same small business world so you can compare them fairly.

## What is ReAct, and why does it work?

ReAct (reason plus act) is the loop wearing its thinking on the outside. Each turn, the model writes a short **thought**, takes one **action** (a tool call), and reads the **observation**, then thinks again with that result in hand. The demo asks "What does teeth whitening cost, and is Friday open?" and you watch the trace alternate: thought, price lookup, observation; thought, calendar lookup, observation; final answer composed from both facts.

The pattern works for a practical reason: it forces the model's reasoning to be *re-grounded* by reality after every step. A model that answers in one shot must hold every fact in its head at once, and any early mistake poisons the whole reply. A ReAct agent that misreads the first observation gets a fresh chance on the next thought, because the trace is a conversation with the world, not a monologue. The price is the usual one: more turns, more calls, and a trace you must cap with a step budget, exactly as in Lesson 09.

## How is plan-and-execute different?

Plan-and-execute moves the thinking to the front. The model first writes the whole plan as an explicit list ("step 1: look up the emergency repair price; step 2: check Saturday"), and only then does execution run the steps in order. The demo's second section shows the plan printed before any tool fires.

The difference sounds small and matters a lot. A written plan can be **inspected before it costs anything**: shown to a human for approval, checked against policy, priced. It also keeps long tasks coherent, because the executor works from the plan rather than re-deciding the mission after every observation. The weakness is rigidity. If step 1's result makes step 2 pointless or wrong, a naive executor ploughs on regardless; production versions add a replanning step after surprises, which is really an admission that pure plan-and-execute and pure ReAct are ends of a dial, and most good systems sit somewhere between them: plan the skeleton, react within the steps.

## What does reflection add?

Reflection bolts a critic onto the end of the work. The agent produces a draft, then evaluates it against checks, then revises. In the demo, a vague first reply to a whitening enquiry is graded against three concrete checks (does it name a specific free slot, does it state the price, is it under 60 words), fails two, and is rewritten to pass all three.

Two things make the demo's version worth copying. The checks are **verifiable**, not "is this good?": a slot time is present or it is not, a price appears or it does not. Vibes-based self-critique produces fluent self-flattery; checklist-based critique produces fixes. And the revision is a full rewrite against the failures, not a patch, which keeps the final text coherent. The cost is real: at minimum a second model call, often a third for the re-check, spent on every output. Spend it where output quality is the product: customer-facing drafts, summaries a human will sign, anything hard to retract. Do not spend it on log lines.

## Run it

```bash
cd 11-planning-and-reasoning-patterns
python3 planning_patterns.py
```

Expected output (abridged; your run prints all three sections in full):

```text
=== 1. ReAct: reason and act, one step at a time ===
question: What does teeth whitening cost, and is Friday open?
  Thought:     I need the whitening price and the Friday calendar. Prices first.
  Action:      price_lookup({'service': 'teeth whitening'})
  Observation: teeth whitening: GBP 299
  ...
  Final answer: Teeth whitening is GBP 299, and Friday has free
                slots at 09:00 and 14:00 if you want to book.

=== 2. Plan-and-execute: the whole plan before any action ===
  plan written up front:
    step 1: price_lookup({'service': 'emergency repair'})
    step 2: calendar_lookup({'day': 'saturday'})
  executing step 1: -> emergency repair: GBP 150
  executing step 2: -> saturday: free slots ['10:00']

=== 3. Reflection: draft, critique, revise ===
  draft:    Hi Ayesha, thanks for your message. We would love to help with whitening some time soon, just let us know what works for you.
  check:    names a specific free slot   FAIL
  check:    states the price             FAIL
  check:    under 60 words               PASS
  revised:  Hi Ayesha, teeth whitening is GBP 299 for a 60 minute session. Friday 14:00 is free if you would like it. Reply to confirm.
  re-check: all checks pass: True
```

## Choosing a pattern, and why this matters in production

Reach for **ReAct** when the path depends on what you find: research, diagnosis, anything where the next question is born from the last answer. Reach for **plan-and-execute** when the steps are knowable in advance and the plan itself is valuable: approvals, audits, predictable multi-part jobs. Reach for **reflection** as a layer, not an architecture: it composes with both of the others, applied to the outputs that carry risk. And notice what all three patterns share: they externalise thinking into text you can read. That is their deepest production value. An agent whose reasoning is a visible trace can be debugged, evaluated (Module 8 builds a whole testing discipline on this), and improved. An agent that "just decides" cannot. When a framework offers you a reasoning pattern, it is really offering you a shape for the trace; judge it on whether that trace tells you the truth.

## Common failures

- **Thoughts that narrate instead of reason.** "Now I will call the tool" is commentary, not thought. A useful thought states what is known, what is missing, and why this action is next. The observation should be able to prove it wrong.
- **Plans with no replanning.** Executing a stale plan into a changed world converts a small surprise into a confidently wrong result, delivered in full.
- **Reflection against vibes.** "Make it better" as the entire critique produces different text, not better text. Every check must be decidable by reading the draft.
- **Reflecting forever.** Cap reflection at one or two rounds. Beyond that, the draft oscillates and the bill grows; a human would have been cheaper.
- **Using all three everywhere.** Patterns compose, but each layer spends calls. The discipline is choosing per task, not maximising machinery per task.

## Recap checklist

- [ ] I can describe ReAct, plan-and-execute, and reflection in one sentence each.
- [ ] I ran all three sections and traced the observations driving each decision.
- [ ] I know which pattern fits a task whose path depends on findings, and which fits a task with knowable steps.
- [ ] I can write reflection checks that are decidable, not vibes.
- [ ] I understand why a visible reasoning trace matters for debugging and evaluation.

## Resources

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629), the original paper (Yao et al.), readable and short, with the traces that named the pattern.
- [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091), the planning-first counterpart paper, for the other end of the dial.
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366), the research root of the reflection pattern.
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents), where these patterns sit in the wider workflow-versus-agent map from Module 3.
- [LangGraph documentation: workflows and agents](https://langchain-ai.github.io/langgraph/tutorials/workflows/), the same patterns as implementable graphs, for when you outgrow hand-rolled loops in Module 7.
