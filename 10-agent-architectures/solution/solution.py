"""Lesson 10 exercise solution: a supervisor that adapts to the work.

The lesson's supervisor always runs the full path: classify, check the
calendar, draft with the model. That wastes effort on enquiries that are
not bookings. This supervisor reads the classification first and
delegates only what the category needs:

  booking  -> check calendar, then a model-drafted offer with a real slot
  research -> skip the calendar, answer from a fixed template, no draft
              call at all (low-value category, template is good enough)

Same fake model underneath, still deterministic. The printout compares
model calls per path, which is the supervisor pattern's real cost story:
structure lets you spend calls only where they change the outcome.

Run:  python3 solution.py
"""

FREE_SLOTS = ["Fri 09:00", "Fri 14:00", "Fri 16:30"]

model_calls = 0


def fake_model(job: str, payload: str) -> str:
    global model_calls
    model_calls += 1
    if job == "classify":
        text = payload.lower()
        if any(word in text for word in ("book", "appointment", "emergency", "pain")):
            return "booking"
        if any(word in text for word in ("cost", "price", "much")):
            return "pricing"
        return "research"
    if job == "draft_booking":
        return "Hi Ayesha, we have Fri 14:00 free for your emergency appointment. Reply to confirm."
    raise ValueError(job)


def template_reply(name: str) -> str:
    """No model call: a fixed, human-written template for low-stakes mail."""
    first = name.split()[0]
    return f"Hi {first}, thanks for looking us up. Shout if you would like a price list, no pressure."


def supervisor(enquiry: dict) -> None:
    global model_calls
    model_calls = 0
    print(f"\nenquiry from {enquiry['name']}: \"{enquiry['message']}\"")
    model_calls += 1  # supervisor planning call
    category = fake_model("classify", enquiry["message"])
    print(f"  supervisor reads classification: {category}")
    if category == "booking":
        slots = FREE_SLOTS
        print(f"  booking path: calendar checked, {len(slots)} free slots")
        reply = fake_model("draft_booking", category)
        print(f"  reply (model-drafted): {reply}")
    else:
        print("  research path: calendar SKIPPED, template reply, no draft call")
        reply = template_reply(enquiry["name"])
        print(f"  reply (template):      {reply}")
    print(f"  model calls used: {model_calls}")


if __name__ == "__main__":
    supervisor(
        {
            "name": "Ayesha Khan",
            "message": "I have tooth pain and need an emergency appointment this week.",
        }
    )
    supervisor(
        {
            "name": "Maria Gomez",
            "message": "I am just researching dentists in the area, no rush.",
        }
    )
    print("\nsame supervisor, two shapes of work, two different costs.")
