# Lesson 31: Anatomy of a Business Assistant

**Time:** 60-75 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 09 (the agent loop), 12 (tool calling), 13 (designing tools), 24 (testing agents)

## The hook

Every service business runs the same quiet leak. An enquiry arrives at 9:40 pm, when nobody is working. It gets answered the next morning, or the day after, or never. The prospect has already booked with whoever replied first. The business did not lose on quality or price. It lost on response time and follow-through.

A business assistant is an agent built to close that leak. It is not a chatbot that makes conversation. It is a small pipeline with a clear job: capture every enquiry, qualify it the same way every time, book the good ones, and follow up the rest until they convert or clearly opt out. This lesson takes that pipeline apart, stage by stage, and runs a complete working version of it.

## The four stages, in plain language

**Capture.** Enquiries arrive through whatever channels the business already has: a website form, Instagram DMs, WhatsApp, email. Capture means one unglamorous thing done perfectly: every enquiry lands in one place, in one shape, exactly once. The "exactly once" part matters. When the same person messages twice, a naive system counts two leads, books two calls, and reports numbers nobody can trust. Deduplication is not a detail. It is the difference between a pipeline and a pile.

**Qualify.** Not every enquiry deserves the same response. Qualification scores each one against what a good customer looks like for this business. This course uses the same eight-signal model across its projects, because a model you can explain beats a model you cannot:

| Signal | Weight | What it asks |
|---|---|---|
| Problem | 20 | Is the pain specific and real? |
| Fit | 20 | Does this business match the offer? |
| Value | 15 | How large is the likely deal? |
| Size | 10 | Can they actually use and support it? |
| Pay | 10 | Do they pay for solutions like this? |
| Access | 10 | Can we reach a decision maker? |
| Urgency | 10 | How soon do they need it? |
| Activity | 5 | Are they engaging right now? |

The total runs 0 to 100 and falls into bands: **HOT at 80+, WARM at 65-79, NURTURE at 50-64**, and COLD below 50. Bands exist so the next stage is a decision, not a debate. Notice what is not in the model: the model's opinion. An LLM can help extract signals from a messy message (you built that skill in Lessons 04 and 12), but the arithmetic, the bands, and the routing are plain deterministic code. When money decisions are questioned later, "the score was 74 because urgency was 6 and access was 6" is an answer. "The AI felt it was promising" is not.

**Book.** HOT and WARM enquiries get offered a real appointment while their attention is still warm. In production this stage talks to an actual calendar through a tool, checks availability, and books only with confirmation. In this lesson it talks to a fake calendar with the same interface, so the pipeline logic is identical and only the adapter changes later. Booking also needs a failure path: if no slot is free, the correct action is to escalate to a human, not to silently drop the hottest lead of the week.

**Follow up.** Most revenue in service businesses hides here. A NURTURE enquiry is a real prospect on the wrong week. The assistant queues it on a ladder: a helpful recap on day 1, one diagnostic question on day 3, a relevant pattern and a call offer on day 7, a final check-in on day 14, then monthly nurture. Each step adds value before it asks for anything, because follow-up that is only "just checking in" trains people to ignore you. COLD enquiries are archived politely. Chasing them burns the sender reputation that the good leads depend on.

## Worked example

Run the reference implementation:

```bash
python3 business_assistant.py
```

Six seeded enquiries go in, including one duplicate. Real output:

```text
capture: skipped duplicate from ops@brightpathdental.example (ENQ-004)

=== Business assistant run ===
ENQ-001  Brightpath Dental      website   score  92  HOT     -> booked Tue 10:00
ENQ-002  Glowhaus Med Spa       instagram score  74  WARM    -> booked Tue 14:00
ENQ-003  Summit Roofing         whatsapp  score  78  WARM    -> booked Wed 09:30
ENQ-005  City Pets Clinic       email     score  56  NURTURE -> added to follow-up queue
ENQ-006  Random Giveaway Page   instagram score   4  COLD    -> archived (below nurture threshold)

Follow-up queue: ['ENQ-005']
Ladder for each queued lead: [1, 3, 7, 14] days
```

Read the code alongside the output. Three design choices to notice. First, signal values are clamped to their weights in `qualify()`, so a bad extraction can never invent a score above 100. Second, the calendar is a class with two methods; everything else in the pipeline is calendar-agnostic. Third, the whole run is deterministic. Same input, same output, every time. That is what makes the evals in Lesson 35 possible.

## Production notes

In production, each stage maps to pieces you have already met in this course. Capture is webhooks and channel APIs (Lesson 06), or an MCP server doing the same job (Lesson 14; TechAura's open-source LeadPipe MCP is this exact pattern, a scored pipeline on Google Sheets and Calendar). Qualification signals come from an LLM extraction step with a strict output contract (Lesson 05), scored by code. Booking is a tool call with the safety habits of Lesson 13: check availability, confirm before writing, make retries safe. Follow-up is a scheduled job with state, not a loop in a chat window, and every message it sends is logged so a human can audit the conversation before a client ever asks.

Approvals belong here too. Many businesses run the assistant in approval mode at first: it drafts bookings and follow-ups, a human approves them in one click, and only after a few clean weeks does it send on its own. That ramp is a feature, not a lack of confidence.

## Common failures

- **Scoring by vibes.** Letting the LLM output the final score directly. Scores drift between runs, nobody can explain a routing decision, and evals become impossible.
- **No deduplication.** The same prospect counted three times, booked twice, and reported as growth.
- **Follow-up with no ladder and no stop.** Either one message and silence, or endless nudges that damage the brand. A ladder with a defined end is the professional middle.
- **Booking without a full-calendar path.** The pipeline works in the demo and drops the best lead of the month in week two.
- **Treating COLD as a challenge.** Low-fit enquiries are archived so attention stays on the bands that pay.

## Recap

A business assistant is four boring stages done reliably: capture everything once, qualify with an explainable score and bands, book the hot and warm, and follow up the nurture band on a ladder that adds value. The intelligence is in the extraction and the conversation. The trust comes from the deterministic spine. Your capstone, starting in Lesson 34, is this pipeline grown into a complete, evaluated, deployed project.

## Resources

- TechAura, LeadPipe MCP (this pattern as an open-source MCP server): https://github.com/techaurah/leadpipe-mcp
- TechAura, AI Lead Automation blueprint (architecture and field mappings): https://github.com/techaurah/ai-lead-automation
- Lesson 13 of this course, Designing tools agents can actually use (booking safety and idempotency)
- Google Calendar API, events and free/busy concepts: https://developers.google.com/calendar/api/guides/overview
- HubSpot, lead scoring concepts and properties: https://knowledge.hubspot.com/properties/create-and-edit-properties
