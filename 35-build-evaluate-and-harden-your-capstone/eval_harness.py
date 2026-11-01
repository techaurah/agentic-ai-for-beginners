"""Outcome eval harness for the capstone business assistant.

Lesson 35, Agentic AI for Beginners (TechAura Academy).

The idea, from Lesson 24: test outcomes, not vibes. Each scenario in
scenarios.json states what must happen (band, action, score where it
matters, total outcome count, bookings after repeated runs) and the
harness checks exactly that against any assistant exposing:

    run(raw_enquiries, calendar) -> outcomes

where each outcome is a dict or an object with enquiry_id, score, band,
action. That is the Lesson 34 contract, so your capstone plugs straight
in: copy this file and scenarios.json next to your project and point
load_assistant() at your package.

Usage:
    python3 eval_harness.py            # evaluates the shipped sample
    python3 eval_harness.py my_module  # evaluates your module instead

Standard library only, deterministic, offline.
"""

from __future__ import annotations

import importlib
import json
import os
import sys


class Calendar:
    """The harness calendar. Deliberately NOT idempotent: booking the
    same enquiry twice consumes two slots, so a careless assistant is
    caught by the re-run scenario. Your assistant owns idempotency."""

    def __init__(self, slots: int):
        self.slots = [f"Slot {i + 1}" for i in range(slots)]
        self.booked: dict[str, str] = {}

    def book_first_free(self, enquiry_id: str) -> str | None:
        for slot in self.slots:
            if slot not in self.booked:
                self.booked[slot] = enquiry_id
                return slot
        return None

    def is_booked(self, enquiry_id: str) -> bool:
        return enquiry_id in self.booked.values()


def _field(outcome, name):
    return outcome.get(name) if isinstance(outcome, dict) else getattr(outcome, name)


def check_scenario(assistant, scenario: dict) -> list[str]:
    failures = []
    calendar = Calendar(scenario.get("slots", 5))
    runs = scenario.get("runs", 1)
    outcomes = []
    for _ in range(runs):
        outcomes = assistant.run(scenario["enquiries"], calendar)

    if len(outcomes) != scenario["expected_total"]:
        failures.append(
            f"expected {scenario['expected_total']} outcome(s), "
            f"got {len(outcomes)}")
    by_id = {}
    for outcome in outcomes:
        by_id.setdefault(_field(outcome, "enquiry_id"), outcome)
    for enquiry_id, expected in scenario["expected_outcomes"].items():
        got = by_id.get(enquiry_id)
        if got is None:
            failures.append(f"{enquiry_id}: no outcome produced")
            continue
        for key in ("band", "action", "score"):
            if key in expected and _field(got, key) != expected[key]:
                failures.append(
                    f"{enquiry_id}: expected {key} {expected[key]!r}, "
                    f"got {_field(got, key)!r}")
    if "expected_bookings_after_all_runs" in scenario:
        actual = len(calendar.booked)
        if actual != scenario["expected_bookings_after_all_runs"]:
            failures.append(
                f"expected {scenario['expected_bookings_after_all_runs']} "
                f"booking(s) after {runs} run(s), got {actual}")
    return failures


def main() -> int:
    module_name = sys.argv[1] if len(sys.argv) > 1 else "sample_assistant"
    assistant = importlib.import_module(module_name)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "scenarios.json"), encoding="utf-8") as fh:
        scenarios = json.load(fh)

    print(f"Evaluating: {module_name}\n")
    passed = 0
    for scenario in scenarios:
        failures = check_scenario(assistant, scenario)
        if failures:
            print(f"FAIL  {scenario['name']}")
            for failure in failures:
                print(f"        - {failure}")
        else:
            print(f"PASS  {scenario['name']}")
            passed += 1
    print(f"\n{passed}/{len(scenarios)} scenarios passed")
    return 0 if passed == len(scenarios) else 1


if __name__ == "__main__":
    raise SystemExit(main())
