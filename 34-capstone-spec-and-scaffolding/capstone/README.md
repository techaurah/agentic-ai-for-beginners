# Capstone scaffolding: the business assistant

This folder is the starting code for your capstone. The full spec lives in the Lesson 34 README one level up. Read it first.

## What is already done

- `assistant/models.py`: data shapes, the eight-signal weights, band thresholds. Complete, do not change the shapes; the Lesson 35 eval harness reads them.
- `assistant/calendar_tool.py`: a complete `FakeCalendar` with idempotent booking, plus the `RealCalendarAdapter` seam for the optional production path.
- `data/seed_enquiries.json`: the six Lesson 31 enquiries, including the duplicate.
- `tests/smoke_test.py`: passes on the untouched skeleton. Run it after every change.

## What you implement

Every function marked `TODO(capstone)`:

| Module | Functions | Spec section |
|---|---|---|
| `assistant/capture.py` | `capture` | 2. Capture and dedupe |
| `assistant/qualify.py` | `score_signals`, `qualify`, `extract_signals` | 3. Qualification |
| `assistant/followup.py` | `plan_followups`, `due_today` | 4. Follow-up ladder |
| `assistant/memory_store.py` | `record_event`, `upsert_enquiry` | 5. Memory and audit |
| `assistant/agent.py` | `run` | 6. Orchestration and routing |

Lesson 31's `business_assistant.py` is a legitimate reference: the capstone is that pipeline grown into modules with state, an audit log, and an eval contract. Understanding it beats copying it, and the eval suite in Lesson 35 includes cases the Lesson 31 version would fail (repeat-contact scoring, idempotent re-runs), so copying alone will not pass.

## Run

```bash
python3 tests/smoke_test.py
```

Standard library only. No keys, no network. Your finished capstone must still pass that bar offline; real integrations go behind the adapter seams and are demonstrated separately.
