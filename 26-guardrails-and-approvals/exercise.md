# Exercise 26: Classify the action nobody planned for

The demo's shift ended with an unlisted action, `export_mailing_list`, pausing for a human because unknown means human. That default is what makes the next change safe to make: new capabilities get added to the classification on purpose, at human tier first, and only graduate to free tiers with evidence.

Work in copies: `my_guardrails.py` and `my_demo.py` (update the import in your demo).

1. **Add a data-export tier.** The clinic wants the agent to prepare a monthly recall list. Add an action `export_customer_data` in a new tier, `data_export`, which behaves like the other human tiers (pauses, decision and reason recorded). Add `export_customer_data` to the demo's job list, and give the scripted human a decision for it: approve, with the reason "monthly recall list, standard report".

2. **Screen for national ID numbers.** Callers paste things they should not. Add a pattern for ID numbers in the shape 123-45-6789 to both `check_input` (block, with a reason that tells the caller what to do instead) and `check_output` (redact). Add one input message and one draft output to the demo that prove both directions work.

3. **Count the cost of the gate.** Extend the shift summary to report how many actions the gate paused for a human during the shift. That number is the price of the safety, and a team that cannot state it will eventually route around the gate.

Acceptance checks:
- `export_customer_data` pauses, is approved by the scripted human, and appears in the audit log with tier `data_export`.
- A message containing a 123-45-6789 style number is blocked at input, and a draft containing one comes out redacted.
- The summary line reports the paused count. For the extended shift it is 5: send_message, refund_payment, delete_records, export_customer_data, and the still-unclassified export_mailing_list all pause. Of those, the human approves the send and the export, and denies the refund, the delete, and the unknown action.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
