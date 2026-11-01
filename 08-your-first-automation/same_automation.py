"""Lesson 08 demo: your first automation, in pure Python.

This is the Python twin of the n8n workflow in workflow.json. Both do the
same job:

  1. take a new enquiry (the trigger)
  2. classify it (in n8n this is a Code node simulating an LLM step,
     because a lesson should never require an API key; here a small
     deterministic stand-in plays the same role)
  3. route on the classification
  4. draft the right next action or reply

Run the n8n version by importing workflow.json into n8n. Run this version
anywhere:  python3 same_automation.py
Fully offline, standard library only, deterministic output.
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
]


def classify(enquiry: dict) -> str:
    """Deterministic stand-in for the LLM classification step.

    A real LLM step returns the same three labels from the same prompt.
    Keeping the labels identical is what lets the rest of the automation
    stay unchanged when you swap the stand-in for a real model.
    """
    text = enquiry["message"].lower()
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


def run(enquiry: dict) -> None:
    category = classify(enquiry)
    reply = draft_reply(enquiry, category)
    print(f"enquiry from {enquiry['name']} via {enquiry['channel']}")
    print(f"  classified as: {category}")
    print(f"  drafted reply: {reply}")


def main() -> None:
    for enquiry in ENQUIRIES:
        run(enquiry)


if __name__ == "__main__":
    main()
