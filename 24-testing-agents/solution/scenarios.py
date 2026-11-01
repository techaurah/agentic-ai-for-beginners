"""Scenario definitions for the outcome test suite.

A scenario is a scripted conversation plus a list of assertions about the
OUTCOME: the final stage, the fields captured, the tools called, the slot
booked, the score, and what the replies must or must not say. Nothing here
grades the wording of a reply beyond a few hard content rules. That is the
QualBench approach: deterministic checks on things a business depends on.

Assertion forms:
    ("stage_is", value)          final stage equals value
    ("field_present", name)      a field was captured
    ("tool_called", name)        a tool was called at least once
    ("booked_hour_is", hour)     the booked slot is exactly this hour
    ("booked_hour_is_not", hour) the booked slot is not this hour
    ("no_booking",)              nothing was booked
    ("score_is", value)          qualification score equals value
    ("reply_contains", text)     some reply contains this text
    ("reply_excludes", text)     no reply contains this text
    ("tool_calls_at_most", tool, n)  a tool was called at most n times
"""

SCENARIOS = [
    {
        "name": "happy-path",
        "title": "Books a free slot when the caller gives full details",
        "turns": [
            "Hi, I would like to book a check-up.",
            "My name is Aisha Khan, my phone is 555-0102.",
            "Please book at 11am.",
        ],
        "assertions": [
            ("stage_is", "booked"),
            ("booked_hour_is", 11),
            ("field_present", "name"),
            ("field_present", "phone"),
            ("field_present", "service"),
            ("score_is", 100),
            ("tool_called", "check_availability"),
            ("tool_called", "book_appointment"),
            ("reply_excludes", "guarantee"),
        ],
    },
    {
        "name": "taken-slot",
        "title": "Refuses a slot that is already booked and offers another",
        "turns": [
            "My name is Marco Ruiz, my phone is 555-0147. I need a cleaning.",
            "Please book at 10am.",
        ],
        "assertions": [
            ("no_booking",),
            ("booked_hour_is_not", 10),
            ("reply_contains", "taken"),
            ("tool_called", "check_availability"),
        ],
    },
    {
        "name": "after-hours",
        "title": "Refuses a booking outside business hours",
        "turns": [
            "My name is Priya Nair, my phone is 555-0119. I need a filling.",
            "Please book at 7pm.",
        ],
        "assertions": [
            ("no_booking",),
            ("stage_is", "collecting"),
            ("reply_contains", "9am and 5pm"),
        ],
    },
    {
        "name": "double-booking",
        "title": "A repeated booking request does not book twice",
        "turns": [
            "My name is Aisha Khan, my phone is 555-0102. I need a check-up.",
            "Please book at 11am.",
            "Please book at 11am.",
        ],
        "assertions": [
            ("stage_is", "booked"),
            ("booked_hour_is", 11),
            ("field_present", "phone"),
            ("tool_calls_at_most", "book_appointment", 1),
        ],
    },
    {
        "name": "missing-phone",
        "title": "Does not confirm a booking without a phone number",
        "turns": [
            "My name is Tom Becker. I would like a whitening appointment.",
            "Please book at 11am.",
        ],
        "assertions": [
            ("no_booking",),
            ("stage_is", "awaiting_details"),
            ("reply_contains", "phone"),
        ],
    },
]
