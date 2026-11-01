"""Follow-up stage: the nurture ladder.

A ladder is a list of steps. Each step adds value before it asks for
anything (Lesson 31). The ladder ends; an assistant that nudges forever
is a liability, not a pipeline.
"""

from __future__ import annotations

from .models import FollowUp

LADDER = [
    {"day": 1, "template": "Hi {name}, thanks for reaching out. Here is a short recap of what you described and one resource that matches it. No pitch, just the recap."},
    {"day": 3, "template": "Hi {name}, one question that decides most of these projects: how are you handling this today?"},
    {"day": 7, "template": "Hi {name}, teams like yours usually see this pattern. If it is useful, I can walk you through it on a short call."},
    {"day": 14, "template": "Hi {name}, last check-in from me. If the timing is wrong, I will close this and you can restart it any time."},
]


def plan_followups(enquiry_id: str, name: str) -> list[FollowUp]:
    """Build the full ladder of FollowUp objects for one enquiry."""
    # TODO(capstone): render LADDER into FollowUp objects for this enquiry.
    raise NotImplementedError("capstone: implement plan_followups()")


def due_today(queue: list[FollowUp], day: int) -> list[FollowUp]:
    """Return the follow-ups due on the given day offset."""
    # TODO(capstone): filter the queue by due_day.
    raise NotImplementedError("capstone: implement due_today()")
