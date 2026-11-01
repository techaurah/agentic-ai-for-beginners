# Lesson 04: Calling models through APIs

**Time:** about 45 minutes · **Difficulty:** Beginner · **Prerequisites:** Lessons 00 and 03

Every agent framework, however grand, is at the bottom a loop making API calls. When a framework's error messages read like magic to you, work becomes superstition: change something, rerun, hope. This lesson removes the magic. You will make a model call by hand, in the plainest possible shape, read everything that comes back, and then make the model return data your code can actually build on. No framework anywhere in sight.

## What does a model API call actually look like?

A request to a chat model API is an HTTP POST with three ingredients: your API key in a header (proof of who pays), a model name, and a list of messages. The response hands back the generated text and a usage object: how many tokens went in, how many came out. That usage object is not decoration. It is your billing meter and your context budget (Lesson 03) made visible, and production code reads it from the first day.

Messages have roles. The **system** message sets standing instructions and identity. **User** messages carry the requests. **Assistant** messages are the model's previous replies. Here is the part beginners miss: the API is stateless. The model remembers nothing between calls, so your code resends the conversation every time. "Memory" in an agent is your code keeping the list and deciding what stays in it, a thread that runs through Module 5.

## Why does code want structured output?

A paragraph is a fine answer for a human and a terrible one for a program. If the next step in your workflow needs the customer's name, urgency, and need as separate values, prose forces you to scrape and guess. Structured output means asking the model to reply as data, usually JSON with named keys, so the reply can be parsed, validated, and routed. The discipline that makes it work has two halves: ask precisely (name the keys, name the allowed values), and then verify anyway (parse it, check the keys, check the values). Lesson 05 hardens this into a pattern that survives bad days. This lesson establishes the shape on a good day.

## The worked example: one client shape, two calls

The file `first_model_call.py` defines the smallest useful client: a `chat` method that takes messages and returns a response with `text`, `prompt_tokens`, and `completion_tokens`. It runs against `FakeModelClient`, a labelled simulation that answers the lesson's two prompts with fixed replies and counts usage honestly as whitespace word counts. Underneath, `call_real_model` contains the same call against a real provider written with `urllib` from the standard library. Read it and compare: the messages your code builds are identical either way. That sameness is the point of a client interface, and it is what lets you swap providers later without rewriting your system (Lesson 30 makes that a cost decision).

Demo A sends a system and user message and prints the reply with its usage. Demo B does the production-shaped call: extract lead details from an enquiry (the same Bright Smiles Dental enquiry the course follows into later modules), demand JSON with four keys, parse it, and validate that the keys exist and urgency is an allowed value.

Run it:

```bash
cd 04-calling-models-through-apis
python3 first_model_call.py
```

Expected output:

```text
DEMO A: a plain call
  Model said: An AI agent uses a model to decide which actions to take, calls tools to take them, and checks the results against a goal.
  Usage (simulated): 20 prompt tokens, 24 completion tokens

DEMO B: structured output you can build on
  Raw reply: {"name": "Dana", "company": "Bright Smiles Dental", "need": "After-hours answering for Instagram messages", "urgency": "high"}
  Parsed lead: {'name': 'Dana', 'company': 'Bright Smiles Dental', 'need': 'After-hours answering for Instagram messages', 'urgency': 'high'}
  Validation: OK (all required keys present, urgency is valid)
  Usage (simulated): 45 prompt tokens, 14 completion tokens
```

Two honest notes on those numbers. They are labelled simulated because the fake counts whitespace words, while a real tokenizer (Lesson 03) would count slightly differently. And Demo B's reply arrived perfectly formed because the fake is polite. Real models are not, reliably, which is exactly tomorrow's lesson.

## Why this matters in production

This small shape, messages in, text and usage out, keys behind an interface, validation at the boundary, is the load-bearing wall of every agent you will ever ship. Teams that internalise it can debug anything a framework does, because they know what the framework is doing underneath. Teams that skip it end up unable to tell a model problem from a plumbing problem, and they pay for both. The usage fields matter commercially too: the difference between a profitable agent service and a money pit is usually visible in per-call token counts weeks before it shows in an invoice.

## Common failures

- **API keys in code or in git.** Keys live in environment variables, never in source. A key committed once is a key rotated, forever.
- **Trusting the reply because it looks like JSON.** If you did not parse it and check it, you did not receive data. You received a rumour.
- **Treating the conversation as the model's memory.** It is your list. When it grows, you pay; when it is trimmed carelessly, the agent "forgets."
- **Ignoring usage until the bill arrives.** Log prompt and completion tokens per call from day one. Future you is grateful (Lesson 28 turns this into tracing).

## Recap checklist

- [ ] I can name the three ingredients of a chat API request and the two halves of the response
- [ ] I can explain the system, user, and assistant roles, and why the API is stateless
- [ ] I ran both demos and can point at where parsing and validation happen
- [ ] I know where a real key would go, and why it never goes in code

## Resources

- [Chat Completions API reference, OpenAI](https://platform.openai.com/docs/api-reference/chat): the canonical request and response shapes this lesson mirrors
- [Structured Outputs guide, OpenAI](https://platform.openai.com/docs/guides/structured-outputs): how a major provider guarantees JSON shape, and its limits
- [Messages API, Anthropic](https://docs.anthropic.com/en/api/messages): the same call in Claude's shape, worth comparing field by field
- [Gemini API documentation](https://ai.google.dev/gemini-api/docs): the third major shape, plus the free tier for experiments
- [urllib.request, Python documentation](https://docs.python.org/3/library/urllib.request.html): how the standard library makes HTTP calls with nothing installed

**Next:** Lesson 05, prompting that survives production: contracts, few-shot examples, and the repair loop.
