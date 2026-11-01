# Lesson 08: Your first automation, an n8n workflow with an LLM step

**Time:** about 45 minutes · **Difficulty:** Beginner · **Prerequisites:** Lessons 06 and 07 (helpful, not required) · **You need:** Python 3.11 or newer for the twin demo. The n8n path needs n8n (free, self-hosted or a trial) but no API key. Everything in this lesson runs with zero credentials.

Time to assemble the plumbing into something a business would recognise. This lesson builds one small, complete automation two ways: as an importable n8n workflow, and as a Python script that does the identical job. The automation takes a new enquiry, classifies it with an LLM-style step, routes on the result, and drafts the right reply. It is the smallest version of the lead-handling systems threaded through this whole course, and building it twice, once visual and once in code, teaches you what each style is actually good for.

One honest note before we start, because it shapes the whole lesson: the classification step is **simulated**. In n8n it is a Code node that returns the same labels a real LLM node would be prompted to return; in Python it is a small deterministic function. This is deliberate. A first lesson that begins with "go get an API key and put a credit card down" loses half its learners before the interesting part, and the automation around the model, the routing, the labels, the reply drafting, is identical whether the classifier is a model or a stand-in. At the end of the lesson you will know exactly which node to swap when you are ready to use a real model.

## What are the moving parts of an automation?

Every useful automation, no-code or code, has the same four bones. A **trigger** starts it: a form submission, a webhook (Lesson 06), a schedule, or, in a learning workflow, a manual run button. **Processing steps** transform the data: classify this, look up that, format the other. A **router** sends the work down different paths based on what the processing found, because a booking request and a pricing question should not get the same reply. And an **action** finishes the job: send a message, write a row of state (Lesson 07), create a booking.

Hold those four words and you can read any workflow diagram in any tool. The n8n canvas is literally these bones drawn as boxes and wires.

## The worked example, both versions

The job: BrightSmile Dental receives an enquiry. The automation classifies it as `booking`, `pricing`, or `research`, then drafts a reply appropriate to the category. A booking gets offered emergency slots, pricing gets the number and a soft next step, research gets a warm low-pressure note.

**The n8n version** lives in `workflow.json`. Its six nodes map one to one onto the bones. "Start (run manually)" is the trigger. "Sample enquiry" stands in for the real trigger payload, shaped exactly like a form submission. "Classify enquiry (simulated LLM)" is the processing step, with a comment block in its code explaining precisely how to replace it with a real LLM node later: same prompt contract, same three output labels. "Is it a booking request?" is the router, an IF node on the category. The two "Draft reply" Code nodes are the actions.

**The Python version** is `same_automation.py`. Same enquiries, same labels, same replies, structured as three functions: `classify()`, `draft_reply()`, and `run()`. Neither version is a translation of the other in any deep sense; they are two expressions of one design, which is the point.

## Run it

Python first, because it needs nothing installed:

```bash
cd 08-your-first-automation
python3 same_automation.py
```

Expected output:

```text
enquiry from Ayesha Khan via website form
  classified as: booking
  drafted reply: Hi Ayesha, sorry to hear that. We have emergency slots this week. Reply with a day that suits you and we will confirm.
enquiry from Tom Lee via instagram
  classified as: pricing
  drafted reply: Hi Tom, teeth whitening is GBP 299 for a 60 minute session. Happy to book you a free consult first if you like.
enquiry from Maria Gomez via email
  classified as: research
  drafted reply: Hi Maria, thanks for looking us up. Shout if you would like a price list or a tour of the clinic, no pressure.
```

For the n8n version: open your n8n instance, choose "Import from File" in the workflow menu, select `workflow.json`, and run it with the manual trigger. The execution view will show the sample enquiry flowing through classification into the booking branch, carrying the drafted reply in its output data. The workflow file is a standard n8n export; its structure (six nodes, every connection pointing at a real node) was verified programmatically when this lesson was written.

## When do you swap in a real LLM step?

When the stand-in's keyword rules start missing real messages, and not before. The swap is small because the contract was kept: the real LLM node gets a prompt like "Classify the enquiry as exactly one of: booking, pricing, research. Reply with the label only", and everything downstream, the router, the replies, the state writes, stays untouched. This is the most useful architectural habit in the course: **keep the model's surface area small and its contract explicit**, so upgrading the model is a node swap, not a rebuild. Module 4 goes deep on this with real tool calling.

## Why this matters in production

The no-code version and the code version will diverge in your career, and knowing both is a genuine professional edge. n8n-style workflows win on visibility: a clinic manager can look at the canvas and understand the business logic, and a change to a reply template takes a minute. Code wins on rigour: version control, tests, review, and behaviour under weird inputs. Serious teams run both, no-code at the business edge and code at the core, connected by webhooks and state exactly like Lessons 06 and 07. What transfers between them is the design: triggers, labels, routing, contracts. Tools change every year; that design vocabulary has been stable for a decade.

One production warning that belongs in a first lesson: this automation drafts replies but does not send them, and that is the correct default. Sending is a separate, deliberate step you add when the drafts have earned trust, ideally behind a human approval step for anything sensitive. Module 8 returns to this with guardrails and human-in-the-loop design.

## Common failures

- **Designing for one happy message.** The demo uses three enquiries on purpose. Test your automations against the awkward inputs, the vague one, the angry one, the empty one, before you trust the routing.
- **Labels that drift.** If the classifier can return "Booking", "booking request", and "urgent" on different days, the router silently misfires. Fix the label set in the prompt contract and validate it in the next step.
- **Putting the whole business in one giant node.** A workflow you cannot read at a glance is a workflow you cannot debug at midnight. Small nodes, named by what they do.
- **Automating the send on day one.** Draft first, review the drafts, then earn the send step. Reversed, this is how businesses apologise on social media.
- **Losing the twin.** When you change logic in the n8n canvas, change the Python twin (or your test fixtures) in the same sitting, or the two will quietly stop describing the same system.

## Recap checklist

- [ ] I can name the four bones of any automation: trigger, processing, router, action.
- [ ] I ran the Python version and matched all three classifications and replies.
- [ ] I imported the n8n workflow (or read its JSON) and traced the booking branch.
- [ ] I know exactly which node becomes the real LLM node, and what its output contract is.
- [ ] I understand why the automation drafts instead of sends, and when that changes.

## Resources

- [n8n: importing and exporting workflows](https://docs.n8n.io/courses/level-one/chapter-6/), how workflow files move between instances.
- [n8n: Code node documentation](https://docs.n8n.io/code/code-node/), the node type used for the simulated LLM step and reply drafting.
- [n8n: IF node documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/), the router used in this workflow.
- [n8n: AI and LLM nodes overview](https://docs.n8n.io/advanced-ai/), the real model nodes you will swap in, from the official docs.
