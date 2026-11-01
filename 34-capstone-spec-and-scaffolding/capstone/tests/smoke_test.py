"""Smoke test for the untouched scaffolding.

Run:  python3 tests/smoke_test.py   (from the capstone/ folder)

This passes on the skeleton as shipped. It checks the parts that are
complete (models, weights, the fake calendar) and the interfaces of the
parts you will implement. When your implementation is done, extend this
file with the acceptance checks from the Lesson 34 checklist.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from assistant.calendar_tool import FakeCalendar          # noqa: E402
from assistant.models import WEIGHTS, band_for            # noqa: E402
import assistant.agent as agent                           # noqa: E402
import assistant.capture as capture                       # noqa: E402
import assistant.followup as followup                     # noqa: E402
import assistant.memory_store as memory_store             # noqa: E402
import assistant.qualify as qualify                       # noqa: E402


def main() -> None:
    assert sum(WEIGHTS.values()) == 100, "scoring weights must total 100"
    assert band_for(92) == "HOT" and band_for(74) == "WARM"
    assert band_for(56) == "NURTURE" and band_for(4) == "COLD"

    cal = FakeCalendar()
    assert cal.book_first_free("ENQ-1") == "Tue 10:00"
    assert cal.book_first_free("ENQ-1") == "Tue 10:00", "booking must be idempotent"
    assert cal.is_booked("ENQ-1") and not cal.is_booked("ENQ-2")

    for module, names in [
        (capture, ["capture"]),
        (qualify, ["score_signals", "qualify", "extract_signals"]),
        (followup, ["plan_followups", "due_today"]),
        (memory_store, ["MemoryStore"]),
        (agent, ["run"]),
    ]:
        for name in names:
            assert hasattr(module, name), f"{module.__name__} is missing {name}"

    print("smoke test passed: scaffolding intact, interfaces present")


if __name__ == "__main__":
    main()
