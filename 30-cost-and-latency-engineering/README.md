# Lesson 30: Cost and Latency Engineering

**Time:** 50-65 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 24 (testing agents), 25 (LLM-as-judge), 28 (observability)

## The hook

Most agents are priced by accident. Someone picked the biggest model during the demo because it gave the best answers, and every step of every run has used it ever since: the frontier model classifies one-word intents, extracts phone numbers, and formats confirmations, all at frontier prices, all day. The invoice is not high because the workload is hard. It is high because nobody ever asked which steps are hard. This lesson asks, with a simulator that makes the asking cheap.

## What does a step actually cost?

An agent run is a chain of **steps**: classify the message, extract the details, draft the reply, reason about the tricky part. Each step is one model call with an input size, an output size, and a price per token that depends on the model. Two facts follow. First, steps differ wildly in difficulty: classification is a solved problem for a small model, while a nuanced complaint reply may genuinely need the frontier. Second, steps differ wildly in volume: the easy ones are usually the frequent ones. Paying frontier prices for the frequent easy steps is the single most common cost defect in production agents, and it is invisible until you price the steps separately, per Lesson 28's traces.

Three levers fix it, in the order this lesson applies them.

**Routing** sends each step type to the cheapest model that clears its quality bar: small models classify and extract, a mid model drafts and summarises, the frontier model only reasons. "Clears its quality bar" is doing real work in that sentence. The bar is measured with Lesson 24's outcome tests and Lesson 25's judge, not assumed. Routing on vibes is how quality quietly dies.

**Caching** exploits repetition. Real traffic asks the same questions all day. An exact-match cache serves repeats at no model cost; providers also offer prompt caching, where a repeated prompt prefix is billed at a fraction of the input price, which suits agents whose long system prompt never changes. Either way, the principle is identical: never pay full price twice for the same computation.

**Batching** trades latency for price on work nobody is waiting for. Providers discount asynchronous batch processing because it fills their idle capacity. Nightly scoring, bulk summaries, and classification of archived conversations are natural batch citizens. A live chat reply is not.

## Worked example

The simulator builds one seeded day of clinic traffic: 120 requests (40 unique, each repeated 3 times, because real traffic repeats), every request a pipeline of steps with token counts drawn from fixed ranges. Prices and latencies are fake, plausible, and printed on the output, so the ratios, not the rates, are the lesson.

```bash
python3 simulator.py
```

```text
strategy                  day cost  avg latency  p95 latency
------------------------------------------------------------
all_frontier            $   1.4013       6793ms      11400ms
all_small               $   0.0627       1987ms       3450ms
routed                  $   0.6167       4457ms       9034ms
routed_cached           $   0.2056       1489ms       7742ms
routed_cached_batched   $   0.1902       1254ms       7253ms
```

Read it as a story in four moves. `all_frontier` is the accidental default: $1.4013 a day. `all_small` is the floor, $0.0627, and it is not a serious candidate on its own, because the reasoning steps are exactly where a small model's failures cost more than the tokens saved. Routing alone takes the day to $0.6167 while keeping the frontier model on every reasoning step. The cache is the dramatic line: because two thirds of the day's traffic is repeats, `routed_cached` falls to $0.2056. Batching the background steps shaves the rest, to $0.1902. The combined effect is a 7.4x reduction, $42.04 a month down to $5.71 on this workload, and latency improves alongside cost, because smaller models and cache hits are also faster.

Two warnings belong inside the celebration. The p95 latency for routed strategies stays high (7253ms even in the best row) because the unlucky request still contains a frontier reasoning step; caching fixes averages faster than it fixes tails, and users remember tails. And every number here is a model of your traffic, not your traffic. Run your own trace file from Lesson 28 through the same arithmetic before promising anyone a saving.

## Why this matters in production

Cost decides which agents survive. A support agent that costs more per conversation than the margin on the booking it creates will be switched off in the first budget review, however good its replies are. Cost engineering is therefore not an optimisation phase after the real work; it is part of the real work, and it compounds with quality work: the eval sets from Lessons 24 and 25 are precisely what let you move a step to a cheaper model with evidence instead of hope. Latency is the same story told in the user's units. Every second of agent thinking is a second the customer spends deciding whether your business is the responsive one.

## Common failures

- **One model for every step, chosen during the demo.** The most expensive default in the field. Price your steps, then choose.
- **Downgrading without an eval.** Moving a step to a small model because it "seems fine" trades a visible cost for an invisible quality loss. Measure first, with the suites you already built.
- **Caching without checking what repeats.** Cache hit rates are a property of your traffic, not of the cache. Measure the repetition before building the machinery.
- **Batching live work.** A discount is not worth a user staring at a spinner. Batch only what nobody is waiting on.
- **Optimising the average, ignoring the tail.** p95 is the latency your unhappiest regular users live with. Watch it in every comparison table.

## Recap

- [ ] Price each step separately; steps differ in difficulty and in volume
- [ ] Route every step to the cheapest model that clears a measured quality bar
- [ ] Cache what repeats: whole responses, and prompt prefixes that never change
- [ ] Batch only the work nobody is waiting for, at the provider's discount
- [ ] Report averages and p95 together; optimise both, trust neither alone
- [ ] Re-run the arithmetic on your own traces before promising savings

## Resources

- [Prompt caching (LangChain Anthropic middleware docs)](https://docs.langchain.com/oss/javascript/integrations/middleware/anthropic): how prefix caching is placed on system prompts, tools, and history in practice
- [Prompt caching guide (Trigger.dev)](https://trigger.dev/docs/ai-chat/prompt-caching): why cache reads cost a fraction of input, and why one changed byte invalidates the prefix
- [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): the measurement discipline that makes downgrading a step a decision instead of a gamble
