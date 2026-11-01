# Lesson 06: APIs and webhooks, how agents touch the real world

**Time:** about 35 minutes · **Difficulty:** Beginner · **Prerequisites:** Lesson 04 (calling models through APIs) · **You need:** Python 3.11 or newer, nothing else. No API keys, no accounts, no internet.

An agent that cannot touch anything outside its own chat window is a demo. The moment an agent books a real appointment, writes to a real CRM, or reacts the second a real lead arrives, it is doing so through the two mechanisms in this lesson: APIs it calls, and webhooks it receives. Every tool you will build in Modules 4 and 5 sits on top of these two ideas, so this lesson uses no framework and no AI at all. Just Python's standard library, so you can see every moving part.

## What is an API, in plain language?

An API is a contract between two programs. One side (the client) sends a structured request, the other side (the server) does work and sends a structured response. When your code calls a model in Lesson 04, it is using an API: your request says "here is the prompt", the response says "here is the completion", and both sides agree on the format in advance.

Three parts of that contract matter for agent work. The **endpoint** is the address, a URL that names the operation, such as `/webhooks/leads`. The **payload** is the data, almost always JSON, travelling in the request or response body. And the **status code** is the server's one-number verdict: 200 means it worked, 400 means your request was malformed, 401 means you failed an identity check, 500 means the server broke. Agents make decisions on status codes, so a well-behaved agent reads them before it reads anything else.

## What is a webhook, and how is it different from calling an API?

A webhook is an API call pointed the other way. Instead of your code asking "has anything happened yet?" every few minutes (that is called polling, and it wastes calls and still reacts late), the other system agrees to call *you* the moment something happens. A form tool POSTs to your endpoint when a lead submits. A payment provider POSTs when an invoice is paid. Your endpoint is just a small program listening for those calls.

For agents this direction matters. A lead automation that polls a form every fifteen minutes answers leads fifteen minutes late. A webhook-driven one reacts in seconds, and speed of response is usually the whole point of the automation. The trade-off is that a listening endpoint is public surface: anyone on the internet can POST to it, which is why the next idea exists.

## How do you know a webhook really came from the provider?

You do not trust the payload; you verify a **signature**. The provider holds a shared secret. Before sending, it runs the exact request body through a keyed hash (HMAC-SHA256) with that secret and puts the result in a header. Your receiver runs the same calculation with the same secret and compares. If one byte of the body changed, or the sender does not know the secret, the signatures differ and you reject the request with a 401 before parsing anything.

Two details separate a toy from a production receiver. First, verify **before** you parse or act, never after. Second, compare with a constant-time comparison (`hmac.compare_digest` in Python) so an attacker cannot guess the signature byte by byte by timing your responses. Our demo does both, on purpose.

## The worked example: a signed webhook round trip

The file `webhook_demo.py` contains both sides of the conversation in one script, so you can watch the full round trip. On the sending side, `send_event()` serializes an event to JSON, signs the raw bytes, and POSTs them with the signature in an `X-Signature` header. On the receiving side, the `WebhookReceiver` class (built on `http.server` from the standard library) reads the body, verifies the signature, and only then parses the event and stores it.

The demo sends the same `lead.created` event twice: once signed with the right secret, once with a wrong one. The code is deliberately small. There is no framework hiding the request, because the request *is* the lesson.

## Run it

```bash
cd 06-apis-and-webhooks
python3 webhook_demo.py
```

Expected output:

```text
receiver: listening on http://127.0.0.1:8765/webhooks/leads
receiver: accepted event 'lead.created' for lead LP-2026-00042 (HTTP 200)
sender:   POST lead.created -> HTTP 200
receiver: REJECTED a request with a bad signature (HTTP 401)
sender:   POST with the wrong secret -> HTTP 401
done: 1 verified event(s) stored
```

Read it as a story. The receiver starts listening. A correctly signed event is accepted and stored, and the sender sees HTTP 200. The same event signed with the wrong secret is rejected with HTTP 401 and never stored, which is why the final count is 1 verified event, not 2.

## Why this matters in production

Almost every failure story in automation is a story from this lesson. Webhooks arrive **more than once** (providers retry until they see a 200), so receivers must be idempotent: storing the same event twice must not book the appointment twice. Webhooks arrive **out of order**, so state updates need to tolerate an "updated" event landing before its "created" event. And endpoints go down, so providers queue and replay, which means your receiver will sometimes get a burst of old events at 3 a.m. Designing for those three facts from day one is the difference between a workflow that survives contact with real customers and one that silently double-books them.

## Common failures

- **Verifying the signature after parsing or acting.** By then the damage is done. Verification is the first thing the handler does, always.
- **Signing the parsed JSON instead of the raw body.** Re-serialized JSON rarely matches byte for byte (spacing, key order), so legitimate events fail verification. Sign and verify the exact bytes.
- **Returning 200 before the work is safely stored.** If you acknowledge and then crash, the provider will never retry and the event is lost. Store first, then acknowledge.
- **Hardcoding the secret.** The demo does it openly for zero-setup learning. In production the secret lives in an environment variable or a secrets manager, and it rotates.
- **Polling where a webhook exists.** Slower, more expensive, and usually the reason an "instant" automation is not instant.

## Recap checklist

- [ ] I can explain the difference between calling an API and receiving a webhook.
- [ ] I can name what the endpoint, payload, and status code each do.
- [ ] I ran the demo and saw one event accepted (200) and one rejected (401).
- [ ] I know why the signature is checked before the body is parsed.
- [ ] I can name the three production realities of webhooks: duplicates, out-of-order delivery, and replays.

## Resources

- [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview), the request and response model everything here sits on.
- [Python docs: http.server](https://docs.python.org/3/library/http.server.html), the standard library server used in the demo.
- [Python docs: hmac](https://docs.python.org/3/library/hmac.html), keyed hashing and `compare_digest`.
- [Stripe: receiving webhooks](https://docs.stripe.com/webhooks), a production-grade treatment of signatures, retries, and idempotency.
- [GitHub: webhooks documentation](https://docs.github.com/en/webhooks), event types and delivery behaviour from a provider you will likely integrate with.
