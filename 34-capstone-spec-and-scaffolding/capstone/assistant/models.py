"""Data models for the capstone business assistant.

These are complete. Your job in the capstone is the behaviour in the
other modules, not the shapes. Keep these shapes stable: the eval
harness in Lesson 35 reads them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Eight-signal scoring model (same as Lesson 31). Weights sum to 100.
WEIGHTS = {
    "problem": 20,
    "fit": 20,
    "value": 15,
    "size": 10,
    "pay": 10,
    "access": 10,
    "urgency": 10,
    "activity": 5,
}

BANDS = ((80, "HOT"), (65, "WARM"), (50, "NURTURE"), (0, "COLD"))


def band_for(score: int) -> str:
    for threshold, name in BANDS:
        if score >= threshold:
            return name
    return "COLD"


@dataclass
class Enquiry:
    id: str
    channel: str            # website | instagram | whatsapp | email
    name: str
    contact: str            # email, handle, or phone: the dedupe key
    message: str
    signals: dict = field(default_factory=dict)   # extracted signal scores
    score: int = 0
    band: str = ""


@dataclass
class Booking:
    enquiry_id: str
    slot: str
    confirmed: bool = False


@dataclass
class FollowUp:
    enquiry_id: str
    step: int               # ladder step index, starting at 0
    due_day: int            # day offset from capture
    message: str


@dataclass
class Outcome:
    """What the assistant decided for one enquiry. The eval unit."""
    enquiry_id: str
    score: int
    band: str
    action: str             # booked | follow_up | archived | escalated
    detail: str = ""
