"""The assistant: orchestration of the four stages.

run() is the contract the Lesson 35 eval harness calls:

    outcomes = run(raw_enquiries, calendar)

It must be deterministic for a given input and calendar state, and it
must return one Outcome per unique enquiry (after dedupe).
"""

from __future__ import annotations

from .calendar_tool import FakeCalendar
from .capture import capture
from .followup import plan_followups
from .models import Outcome
from .qualify import qualify


def run(raw_enquiries: list[dict], calendar: FakeCalendar) -> list[Outcome]:
    """Run capture, qualify, then route by band.

    Routing (spec section 3):
    - HOT and WARM: book. No free slot means action "escalated".
    - NURTURE: action "follow_up", with the ladder planned.
    - COLD: action "archived".
    """
    outcomes: list[Outcome] = []
    # TODO(capstone): orchestrate the stages and build the outcomes.
    # Skeleton of the flow, in order:
    #   for enquiry in capture(raw_enquiries):
    #       qualify(enquiry)
    #       route on enquiry.band ...
    raise NotImplementedError("capstone: implement run()")
    return outcomes
