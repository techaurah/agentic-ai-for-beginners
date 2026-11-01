"""A deliberately imperfect assistant, shipped so the eval harness has
something honest to catch.

It is a plausible first attempt: it scores, it bands, it books. It also
has five real defects, each one a failure mode from Module 10:

  1. No deduplication: a repeat contact becomes a second lead.
  2. No repeat-contact boost (there is nothing to boost; see defect 1).
  3. NURTURE enquiries get booked instead of followed up.
  4. Signal values are not clamped, so a bad extractor can score 792.
  5. A full calendar drops the enquiry silently (no outcome at all),
     and re-running the pipeline double-books.

Your job in Lesson 35 is to read the harness failures, map each one to a
defect here, and make sure YOUR capstone does not share them. Do not fix
this file; it is the specimen, not the patient.
"""

from __future__ import annotations

WEIGHTS = {"problem": 20, "fit": 20, "value": 15, "size": 10,
           "pay": 10, "access": 10, "urgency": 10, "activity": 5}
BANDS = ((80, "HOT"), (65, "WARM"), (50, "NURTURE"), (0, "COLD"))


def _band(score: int) -> str:
    for threshold, name in BANDS:
        if score >= threshold:
            return name
    return "COLD"


def run(raw_enquiries: list[dict], calendar) -> list[dict]:
    outcomes = []
    for raw in raw_enquiries:  # defect 1: no dedupe, every message is a lead
        score = sum(int(raw["signals"].get(k, 0)) for k in WEIGHTS)  # defect 4
        band = _band(score)
        if band == "COLD":
            action = "archived"
        elif band in ("HOT", "WARM", "NURTURE"):  # defect 3: nurture books
            slot = calendar.book_first_free(raw["id"])
            if slot is None:
                continue  # defect 5a: silently dropped, no outcome
            action = "booked"  # defect 5b: never checks existing bookings
        outcomes.append({"enquiry_id": raw["id"], "score": score,
                         "band": band, "action": action})
    return outcomes
