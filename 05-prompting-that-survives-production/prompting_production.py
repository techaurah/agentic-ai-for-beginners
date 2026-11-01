"""
Lesson 05 - Prompting that survives production.

Run it with:

    python3 prompting_production.py

The job: score an incoming sales lead, in code, so a workflow can
route it. Three attempts show the whole lesson:

1. A fragile prompt gets flowing prose back. There is nothing for
   code to hold on to, so the pipeline gets nothing.
2. A production prompt (instructions, few-shot examples, an explicit
   output contract) gets almost-JSON: valid except for a trailing
   comma. Real models do this. Strict parsing still fails.
3. The harness sends ONE repair request quoting the parse error, gets
   clean JSON, validates it, and computes the routing band in code.

The model here is a fake client whose replies are scripted to show
these three behaviours. The harness around it (prompt, parse,
validate, repair, route) is real code, and it is the part that
decides whether your system works in production.
"""

import json


class FakeModelClient:
    """
    SIMULATION. Scripted replies keyed on markers in the prompt:

    - no contract marker: a sloppy prose answer (what a bare prompt
      earns you from a real model on a tired day)
    - OUTPUT_CONTRACT present: JSON with a trailing comma, the single
      most common way real models break strict parsers
    - REPAIR present: the same JSON, clean
    """

    def chat(self, messages):
        joined = "\n".join(message["content"] for message in messages)
        if "REPAIR" in joined:
            return (
                '{"score": 85, "reason": "Urgent and specific need, '
                'named decision maker, weekly losses stated"}'
            )
        if "OUTPUT_CONTRACT" in joined:
            return (
                '{"score": 85, "reason": "Urgent and specific need, '
                'named decision maker, weekly losses stated",}'
            )
        return (
            "Honestly this lead looks hot. They are clearly losing "
            "bookings, Dana sounds ready to buy, and I would score it "
            "around 85 out of 100."
        )


ENQUIRY = (
    "Hi, I am Dana from Bright Smiles Dental. We need someone to answer "
    "our Instagram messages after hours. This is urgent, we are losing "
    "bookings every week."
)

PRODUCTION_PROMPT = """You score incoming sales leads for a service business.

Rules:
- score is an integer from 0 to 100.
- 80 or above: the lead has an urgent, specific problem and a named person.
- 65 to 79: a real need, but no urgency or no named person.
- Below 65: vague, price-shopping, or not a fit.

Examples:
Enquiry: "Our phones ring out every lunch hour and we miss jobs. I am Sam, I run the office."
Output: {"score": 82, "reason": "Urgent and specific problem, named decision maker"}

Enquiry: "Just wondering what your prices are."
Output: {"score": 30, "reason": "Price question only, no problem stated"}

OUTPUT_CONTRACT: Reply with JSON only, keys score (integer 0-100) and reason (one short string). No other text.

Enquiry: """


def band_for(score):
    """The band is computed in code, never trusted from the model."""
    if score >= 80:
        return "HOT"
    if score >= 65:
        return "WARM"
    return "NURTURE"


def validate(payload):
    if not isinstance(payload, dict):
        return "payload is not a JSON object"
    score = payload.get("score")
    if not isinstance(score, int) or not 0 <= score <= 100:
        return f"score is not an integer in 0-100: {score!r}"
    if not isinstance(payload.get("reason"), str) or not payload["reason"]:
        return "reason is missing or empty"
    return None


def main():
    print("Lesson 05 - Prompting that survives production")
    print("===============================================")
    client = FakeModelClient()

    print("\nATTEMPT 1: the fragile prompt")
    reply = client.chat([{"role": "user", "content": f"Score this lead from 0 to 100.\n\n{ENQUIRY}"}])
    print(f"  Model said: {reply}")
    try:
        json.loads(reply)
        print("  Parsed as JSON (unexpected)")
    except json.JSONDecodeError:
        print("  Parse result: FAILED. Prose cannot be parsed as JSON.")
        print("  Pipeline result: nothing usable. A workflow stops here.")

    print("\nATTEMPT 2: the production prompt")
    messages = [{"role": "user", "content": PRODUCTION_PROMPT + ENQUIRY}]
    reply = client.chat(messages)
    print(f"  Model said: {reply}")
    try:
        payload = json.loads(reply)
        print("  Parsed as JSON (unexpected)")
    except json.JSONDecodeError as error:
        print(f"  Parse result: FAILED ({error}).")
        print("  One repair attempt, quoting the error back to the model:")

        repair = (
            "REPAIR: your previous reply was not valid JSON. "
            f"Error: {error}. Reply with JSON only, keys score and reason."
        )
        reply = client.chat(messages + [{"role": "user", "content": repair}])
        print(f"  Model said: {reply}")
        payload = json.loads(reply)

    problem = validate(payload)
    if problem:
        raise SystemExit(f"Validation failed: {problem}")
    result = {
        "score": payload["score"],
        "band": band_for(payload["score"]),
        "reason": payload["reason"],
    }
    print(f"  Validation: OK (score in range, reason present)")
    print(f"  Pipeline result: {result}")
    print("  The workflow can now route this lead on its own.")


if __name__ == "__main__":
    main()
