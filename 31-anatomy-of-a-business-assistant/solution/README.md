# Solution 31: Guard the front door

`my_assistant.py` is the reference pipeline with the two exercise changes.

**Repeat-contact boost.** `capture()` now keeps a `by_contact` map instead of a plain seen-set. When a contact repeats, the existing enquiry is kept (still one lead, still deduped), its message is replaced with the newest one, and its `activity` signal rises by 2, capped at the signal weight of 5 in the scoring model. On the seed data, ENQ-004 merges into ENQ-001 and Brightpath Dental's score moves from 92 to 93. Still HOT, still one booking, but the score now records that this prospect chased the business, which is real buying signal.

One subtlety worth copying: the seed dicts are copied (`dict(raw["signals"])`) before mutation. The original code never mutated its inputs, so it never noticed. The moment capture started editing signals, sharing the dict with the caller's data would have leaked changes back into `SEED_ENQUIRIES` and made repeat runs disagree with first runs. Deterministic pipelines protect their inputs.

**Escalation list.** `run_pipeline()` collects every HOT or WARM enquiry that found no free slot into an `escalations` list with id, name, score, and band, returned alongside the results. Verified behaviour: the calendar holds 5 slots; adding three extra strong enquiries produces 6 booking candidates, 5 bookings, and exactly 1 escalation (the 92-point HOT lead), which is the list an operator works through first each morning.

The design point generalises: every automated stage needs a named human destination for the cases it cannot finish. "Escalate to human" as a log string is a hope. An escalations list with the data a human needs is a system.
