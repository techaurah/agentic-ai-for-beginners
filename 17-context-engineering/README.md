# Lesson 17: Context engineering: fitting the right information into the window

**Time:** 60 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 15 and 16 (short-term and long-term memory)

Prompt engineering asks: how do I phrase this instruction? Context engineering asks the bigger question that decides whether agents work: **what information is in front of the model at this moment, in what order, and what had to be left out?** By this point in the course you have met every ingredient: a system prompt, tool schemas (Lessons 12 to 14), a memory summary (Lesson 16), the recent conversation (Lesson 15), retrieved documents (Module 6 will go deeper), and the user's new message. They all compete for one fixed budget. Context engineering is the discipline of assembling them on purpose.

## What are the parts, and what are they for?

The assembler in `context_assembler.py` names six parts, each with a job:

- **System prompt**: the standing instructions. Short, stable, and always first.
- **Tool schemas**: what the agent can do this turn. Easy to forget they cost tokens on every single call.
- **Memory summary**: the few long-term facts relevant to this user.
- **Retrieved documents**: policy text, knowledge base chunks, whatever retrieval found.
- **Recent turns**: the live conversation, windowed per Lesson 15.
- **User message**: the actual question. The reason the call exists.

Two structural rules fall out of that list. Instructions go first and the question goes last, because models weight the beginning and the end of their input most reliably. And required parts, the instructions and the question itself, are reserved **before** anything optional is packed. An assembler that drops the user's question to make room for a retrieved document has its priorities upside down, and that is not a hypothetical bug: it is what a naive "pack in order until full" loop does at the first tight budget.

## How does the assembler decide?

Each part carries a priority and a required flag. Assembly runs in two passes: required parts first (so they can never be squeezed out), then optional parts in priority order. A part that fits is included. A part that does not fit is truncated with a visible marker if there is room for a useful chunk, or dropped, and every decision lands in a report. The report is the point. Context bugs in production are usually invisible: nobody knows the policy paragraph was dropped until the agent quotes the wrong cancellation terms. A report turns assembly from a hope into an inspectable step.

### How to run it

```bash
cd 17-context-engineering
python3 context_assembler.py
```

The demo assembles the same six parts under a generous budget and a tight one. Expected output:

```text
=== Budget: 400 tokens ===
  system_prompt        23 tokens  included
  tool_schemas         33 tokens  included
  memory_summary       24 tokens  included
  retrieved_policy     62 tokens  included
  recent_turns         27 tokens  included
  user_message         13 tokens  included
  TOTAL               182 tokens

=== Budget: 150 tokens ===
  system_prompt        23 tokens  included
  tool_schemas         33 tokens  included
  memory_summary       24 tokens  included
  retrieved_policy     57 tokens  truncated
  recent_turns         0 tokens  dropped
  user_message         13 tokens  included
  TOTAL               150 tokens
```

Read the tight-budget run as a policy executing: the question survives, the policy survives in truncated form (it contains the cancellation answer the user needs), and the recent turns, nice context but not essential for this question, are what gets sacrificed. Whether you agree with those exact choices is almost beside the point; the point is that they are **choices**, made in code, visible in a report, and changeable in one place.

## Why this matters in production

Most "the model is dumb today" incidents are context incidents: the right document ranked fifth and got cut, the tool list grew until it crowded out the conversation, a memory summary quietly ballooned, or last month's prompt edit pushed a required instruction past the truncation point. Context engineering is how you debug those: budget per part, reserve the essentials, rank retrieval by relevance instead of habit (the exercise), and log the assembly report next to every run. It is also where cost lives. Every token in the context is paid for on every call, so an assembler that packs tightly is a pricing feature, not just a quality one.

## Common failures

- **Packing in fixed order until full.** The tail, often the user's question or the newest instruction, is what silently dies.
- **Retrieving by recency or size instead of relevance.** A long irrelevant document is worse than none: it costs budget and dilutes attention.
- **Letting parts grow without budgets.** Tool schemas and memory summaries expand a little every week until the total no longer fits. Give each part a sub-budget.
- **Invisible truncation.** Cutting text without a marker or a log means the model cannot know its information is partial, and neither can you.
- **One giant system prompt doing every job.** Policies, examples, and facts belong in their own parts, where they can be ranked, budgeted, and tested separately.

## Recap

- [ ] Context engineering decides what the model sees, in what order, under a budget.
- [ ] Instructions first, question last; required parts are reserved before optional ones.
- [ ] Every part gets a priority and effectively a sub-budget; growth is controlled per part.
- [ ] Overflow follows a visible policy: truncate with a marker or drop, and report it.
- [ ] The assembly report is a production debugging tool, not demo decoration.

## Resources

- Anthropic, Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- OpenAI, Prompt engineering guide: https://platform.openai.com/docs/guides/prompt-engineering
- Model Context Protocol (tool schemas are context too): https://modelcontextprotocol.io
- OpenAI, `tiktoken` (counting tokens with the real tokenizer): https://github.com/openai/tiktoken
