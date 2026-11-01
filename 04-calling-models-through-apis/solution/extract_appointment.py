"""
Lesson 04 - Exercise solution: extract an appointment, then validate it.

Same shape as the lesson: a fake client stands in for the model API,
the reply is JSON, and the code refuses to trust it until every field
passes a check, including two format checks (a time pattern and a
phone pattern) that a plain key check would miss.

Run it with:

    python3 extract_appointment.py
"""

import json
import re


class FakeResponse:
    def __init__(self, text, prompt_tokens, completion_tokens):
        self.text = text
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeModelClient:
    """SIMULATION. Deterministic stand-in for a chat model API."""

    def chat(self, messages):
        joined = "\n".join(message["content"] for message in messages)
        if "FORMAT: JSON" in joined:
            reply = (
                '{"service": "cleaning", "customer": "Mr. Patel", '
                '"day": "Friday", "time": "9:30", "phone": "555-0142"}'
            )
        else:
            reply = "Simulated reply: this demo only runs the extraction prompt."
        prompt_tokens = sum(len(m["content"].split()) for m in messages)
        return FakeResponse(reply, prompt_tokens, len(reply.split()))


REQUEST = (
    "Please book a cleaning for Mr. Patel on Friday at 9:30. "
    "His number is 555-0142."
)

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]
TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}$")
PHONE_PATTERN = re.compile(r"^\d{3}-\d{4}$")


def validate(appointment):
    """Return a list of problems. Empty list means the data is usable."""
    problems = []
    for key in ["service", "customer", "day", "time", "phone"]:
        if key not in appointment:
            problems.append(f"missing key: {key}")
    if problems:
        return problems
    if appointment["day"] not in WEEKDAYS:
        problems.append(f"day is not a weekday name: {appointment['day']}")
    if not TIME_PATTERN.match(appointment["time"]):
        problems.append(f"time is not H:MM format: {appointment['time']}")
    if not PHONE_PATTERN.match(appointment["phone"]):
        problems.append(f"phone is not NNN-NNNN format: {appointment['phone']}")
    return problems


def main():
    print("Lesson 04 - Exercise solution: appointment extraction")
    print("=====================================================")
    client = FakeModelClient()
    messages = [
        {
            "role": "system",
            "content": (
                "You extract appointment details from requests. "
                "FORMAT: JSON with keys service, customer, day, time, "
                "phone. Reply with JSON only."
            ),
        },
        {"role": "user", "content": REQUEST},
    ]
    response = client.chat(messages)
    print(f"  Request:   {REQUEST}")
    print(f"  Raw reply: {response.text}")
    appointment = json.loads(response.text)
    problems = validate(appointment)
    if problems:
        raise SystemExit(f"Validation failed: {problems}")
    print(f"  Parsed:    {appointment}")
    print("  Validation: OK (keys present, day, time, and phone formats valid)")


if __name__ == "__main__":
    main()
