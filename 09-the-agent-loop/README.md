# Lesson 09: The agent loop, perceive, decide, act, observe

**Time:** about 40 minutes · **Difficulty:** Beginner to intermediate · **Prerequisites:** Lessons 04 and 05 (model calls and prompting) · **You need:** Python 3.11 or newer. The model in this lesson is a scripted fake, labelled as such, so there are no API keys and no costs.

Everything before this lesson was plumbing: calls, webhooks, state, a fixed automation. This lesson is where the course's title starts to be true. An **agent** is a program that pursues a goal over several steps, choosing its own next action based on what it has seen so far. The mechanism that makes that possible is small enough to fit on one screen, and it is the same mechanism inside every agent framework you will ever use: the agent loop. Learn to see it here, in plain Python, and frameworks stop being magic. They become this loop with better tooling around it.

## What are the four beats of the loop?

**Perceive** means assembling what the agent currently knows: the task, the conversation so far, and the result of its last action, called the **observation**. **Decide** means the model looks at that and picks one next move: call a tool with these arguments, or finish with an answer. **Act** means your code, not the model, executes that move in the real world by calling the tool function. **Observe** means the tool's result is captured and fed back in as the next perception, and the loop turns again.

Two properties of this design do heavy lifting. First, the model never touches the world directly. It proposes actions; your code executes them through tools you wrote, which means you can validate, log, rate-limit, or refuse an action before it happens. Second, the loop terminates on conditions you control: the model declares itself finished, or a maximum step count you set cuts it off. An agent without that second condition is an invoice waiting to happen.

## Why is the model in this lesson fake?

Because the loop is the lesson, and a real model would make every run different. `ScriptedModel` is a test double: a small class with a fixed script that returns the same decisions a real model would be expected to make on this task. It is labelled in the code, and nothing about the loop, the tools, or the safety limits changes when you replace it with a real LLM call that returns the same decision shape. This is also how professionals develop agents: scripted model first, to prove the loop and tools are sound, then the real model, to prove the decisions are good. If you swap the order, you cannot tell whether a failure lives in your machinery or in the model's judgement.

## The worked example: booking a viewing

The task is "Book a viewing for lead LP-2026-00042 on Friday afternoon." The agent has two tools, plain Python functions over a small in-memory calendar: `check_availability(day)` and `book_appointment(day, time, lead_id)`. The script runs in three turns. First the model decides it cannot book blind, so it checks Friday's availability and observes three free slots. Then it picks the first afternoon slot, 14:00, and books it, observing a confirmation. Then, with the confirmation in hand, it decides the goal is met and finishes with a summary. Notice that the model wrote no code and kept no state between calls: the loop carried the observations, and the calendar lived in the tools. That separation is the architecture, and Module 4 is devoted to it.

The loop also carries a hard limit, `MAX_STEPS = 6`. If the model keeps asking for tools without ever finishing, the loop raises an error and stops instead of burning calls forever. In the demo the agent finishes in 3 steps, well inside the limit, which is what healthy traces look like: short, purposeful, and over.

## Run it

```bash
cd 09-the-agent-loop
python3 agent_loop.py
```

Expected output (trimmed here; your run shows every step in full):

```text
task: Book a viewing for lead LP-2026-00042 on Friday afternoon.

[step 1] PERCEIVE: observation = None
[step 1] DECIDE:   I need a free Friday afternoon slot before I can book.
[step 1] ACT:      check_availability({'day': 'friday'})
[step 1] OBSERVE:  {'day': 'friday', 'free_slots': ['09:00', '14:00', '16:30']}

[step 2] DECIDE:   Friday has free slots ['09:00', '14:00', '16:30']. 14:00 is the first afternoon slot.
[step 2] ACT:      book_appointment({'day': 'friday', 'time': '14:00', 'lead_id': 'LP-2026-00042'})
[step 2] OBSERVE:  {'ok': True, 'confirmation': 'BK-1042', 'slot': 'friday 14:00', 'lead_id': 'LP-2026-00042'}

[step 3] FINISH:   Booked LP-2026-00042 into friday 14:00 (confirmation BK-1042).
```

Read the trace top to bottom and check the one thing that makes this an agent rather than a script: the second decision could not have been written in advance, because it depends on the first observation. A script hardcodes 14:00. This agent found it.

## Why this matters in production

The loop is where agent cost, latency, and risk all live. Every turn is a model call, so a task that takes 30 turns costs roughly ten times one that takes 3, and takes ten times as long to fail. Production agent work is mostly loop discipline: tools that return small, decisive observations instead of walls of data; step budgets matched to the task; and traces, like the one this demo prints, stored for every run so that when an agent misbehaves you can read exactly what it perceived and decided, step by step. Module 9 builds the observability habit properly. Without the trace, debugging an agent is astrology.

The loop is also where safety lives. Because your code sits between decide and act, it is the natural place for the guardrails of Module 8: block destructive tools without approval, require confirmation before sending, and kill runs that exceed their budget. None of that is possible in designs where the model acts directly.

## Common failures

- **No step limit.** The single most common beginner omission. Every loop gets a budget, no exceptions, even in demos, so the habit forms before the bills do.
- **Observations that bury the signal.** Returning an entire database table when the model needed one number makes decisions worse and calls pricier. Tools should return the smallest true answer.
- **Tools that hide failure.** A tool that returns success-shaped output when it failed teaches the agent to report false success. Return explicit errors, like this lesson's `{"ok": False, ...}`, and let the loop react.
- **State kept in the model's head.** If a fact matters, it belongs in a tool or in state (Lesson 07), where it can be checked, not in the model's memory of an earlier observation.
- **Mistaking a long trace for a smart agent.** Length is cost. A trace that wanders is a design problem to fix, not a personality to admire.

## Recap checklist

- [ ] I can name the four beats and what each one is responsible for.
- [ ] I ran the demo and can point at the decision that depended on an observation.
- [ ] I know why the model is scripted here, and what swapping in a real one changes (and does not change).
- [ ] I can explain what `MAX_STEPS` protects against.
- [ ] I know why tools must return explicit errors instead of quiet failures.

## Resources

- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents), the loop and its patterns, from a primary source, in plain language.
- [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/), loops, tools, and guardrails framed for builders.
- [Lilian Weng: LLM-powered autonomous agents](https://lilianweng.github.io/posts/2023-06-23-agent/), the widely cited survey post that named the components this lesson implements.
- [Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html), useful when your observations and decisions outgrow plain dictionaries.
