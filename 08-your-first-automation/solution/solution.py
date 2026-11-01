"""Lesson 08 exercise solution: a fourth category, complaint, with handoff.

Pricing and booking enquiries can be answered by the automation. A
complaint cannot, or at least must not be: it goes to a human, fast, with
the full context attached. This adds 'complaint' as a first-class
category, checked FIRST, because a message like 'I want to complain about
my booking' contains the word 'booking' and a naive classifier would
cheerfully draft it a booking reply.

Run:  python3 solution.py
"""

ENQUIRIES = [
    {
        "name": "Ayesha Khan",
        "channel": "website form",
        "message": "I have tooth pain and need an emergency appointment this week.",
    },
    {
        "name": "Tom Lee",
        "channel": "instagram",
        "message": "How much does teeth whitening cost?",
    },
    {
        "name": "Maria Gomez",
        "channel": "email",
        "message": "I am just researching dentists in the area, no rush.",
    },
    {
        "name": "James Osei",
        "channel": "phone transcript",
        "message": "I want to complain about my booking last week, nobody called me back.",
    },
]


def classify(enquiry: dict) -> str:
    """Complaint is checked before booking on purpose: it outranks it."""
    text = enquiry["message"].lower()
    if any(word in text for word in ("complain", "complaint", "unacceptable", "refund")):
        return "complaint"
    if any(word in text for word in ("book", "appointment", "emergency", "pain")):
        return "booking"
    if any(word in text for word in ("cost", "price", "much")):
        return "pricing"
    return "research"


def draft_reply(enquiry: dict, category: str) -> str:
    first_name = enquiry["name"].split()[0]
    if category == "booking":
        return (
            f"Hi {first_name}, sorry to hear that. We have emergency slots "
            "this week. Reply with a day that suits you and we will confirm."
        )
    if category == "pricing":
        return (
            f"Hi {first_name}, teeth whitening is GBP 299 for a 60 minute "
            "session. Happy to book you a free consult first if you like."
        )
    return (
        f"Hi {first_name}, thanks for looking us up. Shout if you would "
        "like a price list or a tour of the clinic, no pressure."
    )


HANDOFF_QUEUE = []


def run(enquiry: dict) -> None:
    category = classify(enquiry)
    print(f"enquiry from {enquiry['name']} via {enquiry['channel']}")
    print(f"  classified as: {category}")
    if category == "complaint":
        HANDOFF_QUEUE.append(enquiry)
        print("  action: HUMAN HANDOFF, no automated reply sent.")
        print(f"  note: queued for a person with the original message attached.")
        return
    print(f"  drafted reply: {draft_reply(enquiry, category)}")


def main() -> None:
    for enquiry in ENQUIRIES:
        run(enquiry)
    print(f"\nhandoff queue: {len(HANDOFF_QUEUE)} complaint(s) waiting for a human")


if __name__ == "__main__":
    main()
