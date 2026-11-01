# Exercise 31: Guard the front door

The reference pipeline trusts its seed data. Real channels are messier. Two changes, both in `business_assistant.py` (copy it to `my_assistant.py` and work there):

1. **Repeat-contact boost, not a duplicate lead.** Right now a second message from the same contact is skipped entirely. Change capture so a repeat contact is still one enquiry, but its `activity` signal is raised by 2 (capped at the weight of 5) and its message is replaced by the newest one. A prospect who chases you is warmer than one who went quiet, and the score should say so.

2. **Full-calendar escalation list.** When the calendar runs out of slots, HOT and WARM enquiries currently get a text note. Change the pipeline result to include an `escalations` list containing every enquiry that needed a human because no slot was free, with its score and band, so an operator has one clear list to work from each morning.

Acceptance checks:
- Running your version still dedupes ENQ-004 into ENQ-001, and ENQ-001 keeps band HOT.
- Adding two extra strong seed enquiries (score 80+) makes the calendar overflow, and both overflow enquiries appear in `escalations`, not in the calendar.
- Nothing else about the output format changes.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
