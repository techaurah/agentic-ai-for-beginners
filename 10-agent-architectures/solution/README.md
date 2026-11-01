# Solution: a supervisor that adapts to the work

Run it with `python3 solution.py`. The two runs end with different counts, on purpose:

```text
enquiry from Ayesha Khan: "I have tooth pain and need an emergency appointment this week."
  supervisor reads classification: booking
  booking path: calendar checked, 3 free slots
  reply (model-drafted): Hi Ayesha, we have Fri 14:00 free for your emergency appointment. Reply to confirm.
  model calls used: 3

enquiry from Maria Gomez: "I am just researching dentists in the area, no rush."
  supervisor reads classification: research
  research path: calendar SKIPPED, template reply, no draft call
  reply (template):      Hi Maria, thanks for looking us up. Shout if you would like a price list, no pressure.
  model calls used: 2
```

## What changed, and why

**The classification became a routing decision, not just a label.** In the lesson the category was computed and then largely admired. Here it controls real behaviour: which tools run, and whether the most expensive component, the drafting model, is invoked at all. That is the supervisor pattern earning its coordination call. A coordinator that always delegates everything to everyone is overhead; a coordinator that delegates *conditionally* is a cost and quality strategy.

**The template reply is a feature, not a failure of ambition.** Research enquiries are high volume and low stakes. A template is instant, costs nothing, and reads identically every time, which for a low-stakes acknowledgement is better than a model draft that varies. Mature systems are full of these deliberate non-uses of AI at exactly the points where AI adds cost without adding outcome. Knowing where *not* to spend a call is most of production agent economics.

**The counts make the argument auditable.** Three calls where the money is (a patient in pain, a bookable slot), two where it is not. When someone proposes a fancier architecture, this is the table to ask for: model calls per completed task, per category, before and after.
