"""Calendar tool: the booking stage's only view of the outside world.

FakeCalendar is complete and is what your tests and the Lesson 35 eval
harness run against. RealCalendarAdapter is the production seam: same
two methods, real API behind them.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FakeCalendar:
    slots: list[str] = field(default_factory=lambda: [
        "Tue 10:00", "Tue 14:00", "Wed 09:30", "Wed 13:00", "Thu 11:00",
    ])
    booked: dict = field(default_factory=dict)  # slot -> enquiry id

    def book_first_free(self, enquiry_id: str) -> str | None:
        """Book and return the first free slot, or None if full.

        Booking the same enquiry twice returns its existing slot instead
        of consuming a second one (idempotent, Lesson 13).
        """
        for slot, holder in self.booked.items():
            if holder == enquiry_id:
                return slot
        for slot in self.slots:
            if slot not in self.booked:
                self.booked[slot] = enquiry_id
                return slot
        return None

    def is_booked(self, enquiry_id: str) -> bool:
        return enquiry_id in self.booked.values()


class RealCalendarAdapter:
    """Production seam. Same interface as FakeCalendar.

    Wire this to a real calendar API (for example Google Calendar) using
    the patterns from Lesson 06 and Lesson 13: check availability first,
    write once with an idempotency key, confirm the write by reading it
    back. Credentials come from the environment, never from code.
    """

    def __init__(self, calendar_id: str):
        self.calendar_id = calendar_id

    def book_first_free(self, enquiry_id: str) -> str | None:
        # TODO(capstone, optional): implement against a real calendar.
        raise NotImplementedError("optional: wire a real calendar")

    def is_booked(self, enquiry_id: str) -> bool:
        # TODO(capstone, optional): implement against a real calendar.
        raise NotImplementedError("optional: wire a real calendar")
