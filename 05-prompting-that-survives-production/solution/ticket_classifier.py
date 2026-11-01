"""
Lesson 05 - Exercise solution: classify a support ticket, in code.

Same production pattern as the lesson (contract, parse, validate,
one repair), pointed at a new job: support ticket triage. The scripted
model fails in a different, subtler way this time. Its JSON parses,
but confidence arrives as the string "high" instead of a number, so
only the validation step catches it. Syntax checks alone would have
let it through and broken the routing code downstream.

Run it with:

    python3 ticket_classifier.py
"""

import json


class FakeModelClient:
    """
    SIMULATION. Scripted replies:

    - OUTPUT_CONTRACT present: valid JSON, wrong type for confidence
    - REPAIR present: the same classification, with a numeric confidence
    """

    def chat(self, messages):
        joined = "\n".join(message["content"] for message in messages)
        if "REPAIR" in joined:
            return (
                '{"category": "billing", "confidence": 0.92, '
                '"summary": "Duplicate charge on the March invoice, '
                'refund requested"}'
            )
        if "OUTPUT_CONTRACT" in joined:
            return (
                '{"category": "billing", "confidence": "high", '
                '"summary": "Duplicate charge on the March invoice, '
                'refund requested"}'
            )
        return "Sounds like a billing problem to me."


TICKET = "My card was charged twice for the March invoice and I need a refund."

PROMPT = """You classify support tickets for a small software company.

Categories: billing, technical, account, other.

Examples:
Ticket: "The app crashes every time I export a report."
Output: {"category": "technical", "confidence": 0.88, "summary": "App crashes on report export"}

Ticket: "I cannot log in since I changed my email address."
Output: {"category": "account", "confidence": 0.9, "summary": "Login broken after email change"}

OUTPUT_CONTRACT: Reply with JSON only, keys category (one of billing, technical, account, other), confidence (a number from 0 to 1), summary (one short string). No other text.

Ticket: """

CATEGORIES = ("billing", "technical", "account", "other")


def validate(payload):
    """Type and range checks. Returns a problem string, or None."""
    if not isinstance(payload, dict):
        return "payload is not a JSON object"
    if payload.get("category") not in CATEGORIES:
        return f"category is not one of {CATEGORIES}: {payload.get('category')!r}"
    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return f"confidence is not a number: {confidence!r}"
    if not 0 <= confidence <= 1:
        return f"confidence is outside 0-1: {confidence}"
    if not isinstance(payload.get("summary"), str) or not payload["summary"]:
        return "summary is missing or empty"
    return None


def main():
    print("Lesson 05 - Exercise solution: ticket classification")
    print("====================================================")
    client = FakeModelClient()
    messages = [{"role": "user", "content": PROMPT + TICKET}]

    reply = client.chat(messages)
    print(f"\n  Ticket: {TICKET}")
    print(f"  Model said: {reply}")
    payload = json.loads(reply)
    print("  Parse result: OK, the JSON is syntactically valid.")

    problem = validate(payload)
    if problem:
        print(f"  Validation: FAILED ({problem}).")
        print("  One repair attempt, quoting the problem back to the model:")
        repair = (
            "REPAIR: your previous reply failed validation. "
            f"Problem: {problem}. Reply with JSON only, keys category, "
            "confidence (a number from 0 to 1), summary."
        )
        reply = client.chat(messages + [{"role": "user", "content": repair}])
        print(f"  Model said: {reply}")
        payload = json.loads(reply)
        problem = validate(payload)
        if problem:
            raise SystemExit(f"Validation failed again: {problem}")

    print("  Validation: OK (category known, confidence is a number in 0-1)")
    print(f"  Pipeline result: {payload}")
    print("  The ticket can now be routed to the billing queue on its own.")


if __name__ == "__main__":
    main()
