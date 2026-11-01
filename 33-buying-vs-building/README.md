# Lesson 33: Buying vs Building

**Time:** 40-50 minutes · **Difficulty:** Beginner · **Prerequisites:** Lessons 31 and 32

## The hook

Every company that wants an agent faces the same fork in the road, and both directions are lined with people happy to sell them the wrong one. Build it yourself and you own everything, including the 9 pm incidents. Buy it as a service and someone else carries the operations, including, if you are careless, your data and your exit. This lesson gives you a scoring framework for making the call with numbers instead of sales pressure, in either direction. It ends Module 10, the company track, and it is written to be used in a real meeting.

## The decision, in plain language

Strip the marketing off and the choice is between **buying an outcome** and **building a capability**.

Buying an outcome (the operated service of Lesson 32) means: the pipeline runs, enquiries get answered, bookings happen, and a specialist team monitors, tunes, and improves it. You get speed and accountability. You give up some control, and you must protect yourself with ownership and exit terms.

Building a capability means: your team designs, builds, and runs the agent. You get full control, full customisation, and a skill that compounds across every future project. You also get the whole cost structure from Lesson 32, paid in your own salaries: monitoring, tuning, incident response, and the improvement rhythm, forever, at whatever your team's loaded hourly rate really is.

Neither is the smart option in general. Each is the smart option for a specific company at a specific moment. The framework below exists because "it depends" is true and useless; this makes what it depends on explicit.

## The framework

Open `decision-framework.md`. Ten factors, each scored 1 to 5: five that favour buying (speed needed, no internal builder, process stability, standard shape, operational cost of failure) and five that favour building (strategic capability, internal expertise, data sensitivity, integration depth, volume economics). Total each side. Buy leads by 6 or more: buy. Build leads by 6 or more: build. Within 5: hybrid, which usually means an operator builds and runs the first version while your team shadows and takes over piece by piece, with the handover written into the contract from day one.

Run the script to watch it work on two fictional companies chosen to be opposites:

```bash
python3 score_decision.py
```

```text
Brightpath Dental Group (fictional)
  buy 24/25   build 7/25   -> BUY: use an operated service. Negotiate ownership and exit terms.

Northgate Logistics (fictional)
  buy 10/25   build 24/25   -> BUILD: develop in-house. Budget for the run, not just the build.
```

Brightpath is the Lesson 31 pattern exactly: a standard capture-qualify-book-follow-up shape, revenue leaking tonight, nobody technical on staff. Building would take them months to reach what a service runs in weeks, and then the maintenance lands on a practice manager. Northgate is the mirror image: agent skill is strategic for them, they employ platform engineers, the agent must live inside proprietary dispatch systems, and their volume makes in-house operation cheaper at scale. A service would fight their architecture and their ambitions at the same time.

Notice the factors that did the work. It was not price. It was speed, capability strategy, and integration depth. In real decisions it usually is.

## The three questions that override the arithmetic

The worksheet ends with three questions, and they outrank the totals:

1. **If this agent stopped working tonight, who notices first, and when?** If the honest answer is "a customer, next week", then whoever runs it needs monitoring that does not exist yet. That fact alone has settled many buy decisions.
2. **Is the process written down anywhere?** An agent encodes a process. An undocumented process gets encoded as someone's guess, bought or built, and the debugging is billed either way.
3. **In twelve months, do you want to own an agent, or own agent-building skill?** Different purchases, different prices, different regrets. Companies that confuse them buy an agent, resent the fee, cancel, and end with neither.

## For developers: what this means for you

If you are a developer reading a company-track lesson, this framework is your map of the market you will work in. Employers on the build side of this line are your future teams; companies on the buy side are your future clients and employers' clients. The capstone that starts next lesson is deliberately the Brightpath shape, because that standard pattern is where most real agent work, bought or built, actually happens. Being the person who can build it, evaluate it, and also explain this framework in a meeting is a genuinely rare combination. That is the person this course is trying to produce.

## Common failures

- **Comparing build cost to service price.** The build quote is compared with twelve months of service fees, and the run costs (Lesson 32: the humans dominate) never enter the spreadsheet.
- **Scoring aspirationally.** "We could hire an engineer" scored as expertise 4. Score the team you have, not the team in the plan.
- **Ignoring the hybrid middle.** Buy-versus-build framed as permanent and binary, when sequencing (service now, capability over a year) is often the correct answer.
- **Letting the loudest vendor hold the pen.** If the person scoring your worksheet sells one of the options, ask who benefits from each 5.

## Recap

Buy an outcome or build a capability; score ten factors honestly; let speed, strategy, and integration depth carry their real weight; and ask the three overriding questions before signing anything. Module 10 is complete: you can now describe a business assistant's anatomy, explain what running one as a service actually involves, and advise a company on which side of the line it sits. Next, you build the whole thing. The capstone starts in Lesson 34.

## Resources

- The worksheet in this lesson: `decision-framework.md`, applied by `score_decision.py`
- Lesson 32 of this course, Agents as a Service (the cost structure and ownership lines behind the buy column)
- TechAura, Agent as a Service offer page (one operator's public terms, useful as a comparison document): https://techaurah.com/agent-as-a-service
- McKinsey, "The State of AI" reports (how organisations report build versus buy patterns, updated yearly): https://www.mckinsey.com/capabilities/quantumblack/our-insights/state-of-ai
- Gartner, build vs buy decision coverage for AI platforms: https://www.gartner.com/en/information-technology
