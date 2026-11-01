"""A tiny deterministic stand-in for a clinic booking agent.

A real agent calls an LLM, and the wording of its replies changes from run
to run. Its outcomes should not. This module models the part you can test:
given a scripted conversation, what did the agent capture, which tools did
it call, what did it book, and what stage did the conversation end in?

Two variants share one interface:

- FrontDeskAgent()          the careful version
- FrontDeskAgent(buggy=True) the same agent with three realistic defects:
  it books taken and after-hours slots, it never records the phone number,
  and its confirmation promises a "guarantee" the clinic cannot make.

The harness in harness.py runs the same scenarios against both, so you can
watch assertions catch behaviour instead of vibes.
"""

import re

BUSINESS_START = 9        # first booking starts at 09:00
LAST_START = 16           # last booking starts at 16:00 (clinic closes 17:00)
TAKEN_HOURS = {10, 14}    # already booked on the fake calendar
SERVICES = ("check-up", "cleaning", "filling", "whitening")

NAME_RE = re.compile(r"my name is ([A-Za-z]+ [A-Za-z]+)", re.IGNORECASE)
PHONE_RE = re.compile(r"(\d{3}-\d{4})")
TIME_RE = re.compile(r"at (\d{1,2})(?::\d{2})?\s*(am|pm)", re.IGNORECASE)


def _hour_24(hour, meridiem):
    hour = int(hour)
    if meridiem.lower() == "pm" and hour != 12:
        hour += 12
    if meridiem.lower() == "am" and hour == 12:
        hour = 0
    return hour


def _fmt(hour):
    suffix = "am" if hour < 12 else "pm"
    return f"{hour if hour <= 12 else hour - 12}{suffix}"


class FrontDeskAgent:
    def __init__(self, buggy=False):
        self.buggy = buggy
        self.fields = {}
        self.tool_calls = []
        self.booked_hour = None
        self.stage = "collecting"
        self.replies = []

    # -- internals ------------------------------------------------------

    def _extract(self, text):
        name = NAME_RE.search(text)
        if name:
            self.fields["name"] = name.group(1)
        if not self.buggy:
            phone = PHONE_RE.search(text)
            if phone:
                self.fields["phone"] = phone.group(1)
        # The buggy variant silently never records the phone. Field
        # assertions in the suite exist to catch exactly this class of bug.
        for service in SERVICES:
            if service in text.lower():
                self.fields["service"] = service

    def _score(self):
        # A qualification score built from captured fields, not from the
        # model's confidence. Name 40, phone 30, service 30.
        return (
            (40 if "name" in self.fields else 0)
            + (30 if "phone" in self.fields else 0)
            + (30 if "service" in self.fields else 0)
        )

    def _book(self, hour):
        self.tool_calls.append({"tool": "book_appointment", "hour": hour})
        self.booked_hour = hour
        self.stage = "booked"

    def _confirm(self, hour):
        msg = (
            f"Booked: {self.fields.get('service', 'appointment')} at "
            f"{_fmt(hour)} for {self.fields.get('name', 'you')}."
        )
        if self.buggy:
            msg += " We guarantee a pain-free result, every time."
        return msg

    # -- public API -----------------------------------------------------

    @property
    def score(self):
        return self._score()

    def handle(self, text):
        """Process one user message and return the agent's reply."""
        self._extract(text)
        match = TIME_RE.search(text)
        wants_booking = "book" in text.lower() and match is not None

        if not wants_booking:
            reply = "Happy to help. What would you like to book, and when?"
            self.replies.append(reply)
            return reply

        hour = _hour_24(match.group(1), match.group(2))

        if not self.buggy and self.stage == "booked" and hour == self.booked_hour:
            # Idempotency guard (exercise fix): a repeat request for the
            # slot this caller already holds is a confirmation, not a
            # second booking. No tool calls, no second calendar entry.
            reply = (
                f"That slot is already yours: you are booked in at "
                f"{_fmt(hour)}. Anything else I can help with?"
            )
            self.replies.append(reply)
            return reply

        self.tool_calls.append({"tool": "check_availability", "hour": hour})
        taken = hour in TAKEN_HOURS
        in_hours = BUSINESS_START <= hour <= LAST_START

        if self.buggy:
            # Defect: books whatever was asked for, checks nothing that
            # matters, and does not wait for the phone number.
            self._book(hour)
            reply = self._confirm(hour)
            self.replies.append(reply)
            return reply

        if taken:
            free = next(
                h for h in range(BUSINESS_START, LAST_START + 1)
                if h not in TAKEN_HOURS and h != self.booked_hour
            )
            reply = (
                f"{_fmt(hour)} is already taken. The next free slot is "
                f"{_fmt(free)}. Would you like that one?"
            )
        elif not in_hours:
            reply = (
                "We take bookings between 9am and 5pm, with the last "
                "appointment starting at 4pm. Would a time in that window "
                "work for you?"
            )
        elif "name" not in self.fields or "phone" not in self.fields:
            self.stage = "awaiting_details"
            missing = "name" if "name" not in self.fields else "phone number"
            reply = (
                f"I can hold {_fmt(hour)} for you. I just need your "
                f"{missing} before I confirm the booking."
            )
        else:
            self._book(hour)
            reply = self._confirm(hour)

        self.replies.append(reply)
        return reply

    def transcript(self):
        """Everything an outcome test is allowed to look at."""
        return {
            "stage": self.stage,
            "fields": dict(self.fields),
            "tool_calls": [c["tool"] for c in self.tool_calls],
            "booked_hour": self.booked_hour,
            "score": self.score,
            "reply_text": " ".join(self.replies).lower(),
        }
