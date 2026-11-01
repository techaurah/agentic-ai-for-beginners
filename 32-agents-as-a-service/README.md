# Lesson 32: Agents as a Service

**Time:** 45-60 minutes · **Difficulty:** Beginner-Intermediate · **Prerequisites:** Lesson 31 (anatomy of a business assistant); Lessons 27-30 (production module) help but are not required

## The hook

Here is a sentence you will hear in every sales conversation about agents this year: "Why would I pay monthly for something I can build once?" It sounds reasonable. It is also based on a misunderstanding of what an agent is. An agent is not a document you finish. It is an operation you run, closer to a phone line or a bookkeeper than to a piece of software on a shelf. This lesson explains the operating model honestly: what it actually costs to run an agent for a company month after month, what the company owns, what the operator does, and where this model is the wrong choice.

## What "agents as a service" means

Agents as a Service (AaaS) means a specialist team designs, builds, deploys, monitors, and improves an agent for a business, for a recurring fee, instead of handing over code and leaving. TechAura runs its Agentic AI offer this way, and this lesson teaches the model the way we explain it to clients, including the parts that argue against us.

The pattern is not new. Businesses already buy operations as a service everywhere: payroll, bookkeeping, managed hosting, IT support. In each case the buyer is not purchasing a thing. They are purchasing an outcome that keeps happening: staff paid correctly, servers patched, phones answered. An agent that captures, qualifies, books, and follows up (Lesson 31) is the same shape. The outcome is "no enquiry goes unanswered and no warm lead goes cold." That outcome has to be produced every day, including the days the model provider changes a price, a channel changes its API, or the business changes its offer.

## What it actually costs to run one

Run the worksheet:

```bash
python3 operating_costs.py
```

Every number in it is illustrative, and the script says so at the top, because prices change and labour rates depend on your market. The structure is the lesson:

```text
Model usage                            $    5.76
Hosting                                $   25.00
Tools and data                         $   40.00
Phone and messaging                    $   30.00
Human operations (review, tuning)      $  160.00
Monthly improvement work               $   80.00
Contingency                            $   34.08
TOTAL per month                        $  374.84
Cost per enquiry                       $    0.94
```

Look at the first line. Four hundred enquiries a month, handled end to end, cost under six dollars in model tokens at mid-tier prices. The model is nearly free. The real costs are everything around it: hosting, the calendar and CRM tiers, phone and messaging fees, and above all the human hours. Someone reviews the escalation queue each morning. Someone reads the traces when a conversation goes sideways (Lesson 28), tunes the prompts when the business changes its pricing, checks that follow-ups still sound like the brand, and runs a monthly improvement pass so the agent gets better instead of slowly drifting worse as the business moves and it does not.

That is the honest core of AaaS: **the client is not paying for tokens. They are paying for the operation** (the monitoring, the tuning, the accountability when something breaks at 9 pm) bundled with the agent itself.

## Who owns what

This is the question serious buyers ask, and vague answers kill deals. A fair AaaS arrangement states it plainly:

- **The client owns their data**: enquiries, conversations, customer records, and the exports of all of it, at any time, in usable formats.
- **The client owns their configuration**: prompts written for their business, their scoring weights, their templates and brand voice, documented well enough to hand over.
- **The operator owns their platform and general tooling**: the reusable pipeline, integrations, and know-how they bring to every client, the same way an accounting firm owns its practice software.
- **Exit is defined up front**: what gets handed over, in what format, over what period, if the service ends. An operator who will not write the exit down is telling you something.

If you buy agents as a service, negotiate these four points before price. If you sell it, publish them before you are asked. Both sides do better when the ownership lines are boring and clear.

## When AaaS is the wrong choice

Honesty cuts both ways, and a course that only sells is a brochure. Running agents as a service is usually the wrong call when:

- **Volume is tiny.** Five enquiries a month do not need an operated agent; a good form and a shared inbox will do.
- **The process changes weekly.** An agent encodes a process. If the business reinvents its offer every month, the tuning bill eats the value, and the honest advice is to stabilise the process first.
- **The team wants the capability, not the outcome.** Some companies should build internal skill (Lesson 33 gives them the framework). A good operator says so, because a client who stays for the wrong reason churns angry.
- **The work is deeply regulated or sensitive.** Some conversations must stay inside the company's own walls and staff, full stop.

## Production notes, for the developers reading

Operating agents for other companies multiplies every production lesson in Module 9 by the number of clients. Per-client isolation of data and credentials, per-client configuration instead of per-client code forks, tracing tagged by client so one bill and one audit trail per business, and a hard rule that one client's incident never leaks another client's data into a log line. The operators who survive are the ones whose monitoring notices a broken agent before the client does. That is a higher bar than building one agent for yourself, and it is exactly the bar the monthly fee is claiming to meet.

## Common failures

- **Selling the build, forgetting the run.** A one-off handover with no monitoring: the agent degrades silently and the client concludes agents do not work.
- **Pricing from token costs.** Quoting from the $5.76 line and discovering the human operations in month two. The worksheet exists to prevent exactly this.
- **Lock-in by obscurity.** Keeping prompts and configuration undocumented so the client cannot leave. Short-term retention, long-term reputation damage, and increasingly a procurement red flag.
- **No improvement rhythm.** An agent that is never tuned is a snapshot of the business on launch day. The market moves; the snapshot does not.

## Recap

An agent is an operation, not a deliverable. Agents as a Service exists because running that operation well (monitoring, tuning, improving, being accountable at 9 pm) is real, recurring work that most businesses would rather buy than staff. The model only deserves to exist when the ownership lines are explicit, the exit is written down, and the operator tells the wrong-fit client not to buy. Next lesson: the framework for making that buy-or-build call yourself.

## Resources

- The worksheet in this lesson: `operating_costs.py` and `operating-cost-worksheet.csv` (illustrative inputs; replace with your own quotes)
- Lesson 28 of this course, Observability: tracing agent runs and tracking cost
- TechAura, Agent as a Service (how one operator describes the offer publicly): https://techaurah.com/agent-as-a-service
- Anthropic, building effective agents (why simple, well-understood systems beat heavy frameworks in operations): https://www.anthropic.com/research/building-effective-agents
- OpenAI, a practical guide to building agents: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
