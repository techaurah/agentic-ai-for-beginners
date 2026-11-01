"""
Lesson 04 - Calling a model through an API, offline.

Run it with:

    python3 first_model_call.py

A model API call is just a request with messages and a response with
text plus a usage count. This file defines the smallest useful client
shape, then runs it against FakeModelClient: a deterministic stand-in
that behaves like a real API (messages in, text and usage out) without
network or keys. At the bottom, call_real_model() shows the same call
against a real provider using only the standard library. Swap the
client, keep the rest of your code: that is the whole trick.
"""

import json
import os
import urllib.request


class FakeResponse:
    """What a chat API hands back: the text, and what it cost."""

    def __init__(self, text, prompt_tokens, completion_tokens):
        self.text = text
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeModelClient:
    """
    SIMULATION. A deterministic stand-in for a chat model API.

    It recognises the two demo requests below and answers with fixed
    text, the way a real model would on a good day. Token counts are
    honest whitespace word counts of the actual strings, labelled as
    simulated because a real tokenizer would count slightly differently.
    """

    def chat(self, messages):
        joined = "\n".join(message["content"] for message in messages)
        if "FORMAT: JSON" in joined:
            reply = (
                '{"name": "Dana", "company": "Bright Smiles Dental", '
                '"need": "After-hours answering for Instagram messages", '
                '"urgency": "high"}'
            )
        elif "what does an AI agent do" in joined:
            reply = (
                "An AI agent uses a model to decide which actions to "
                "take, calls tools to take them, and checks the results "
                "against a goal."
            )
        else:
            reply = (
                "Simulated reply: the fake client only knows the two "
                "demo prompts in this lesson."
            )
        prompt_tokens = sum(len(m["content"].split()) for m in messages)
        completion_tokens = len(reply.split())
        return FakeResponse(reply, prompt_tokens, completion_tokens)


def call_real_model(messages):
    """
    The same call against a real provider (OpenAI-compatible shape).

    Reference code only: the demo never calls this, so the lesson runs
    offline. To use it for real, set OPENAI_API_KEY, install nothing
    (urllib is standard library), and pass the same messages list you
    would pass to FakeModelClient.
    """
    api_key = os.environ["OPENAI_API_KEY"]
    payload = json.dumps(
        {"model": "gpt-4o-mini", "messages": messages}
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read())
    return data["choices"][0]["message"]["content"]


ENQUIRY = (
    "Hi, I am Dana from Bright Smiles Dental. We need someone to answer "
    "our Instagram messages after hours. This is urgent, we are losing "
    "bookings every week."
)


def demo_plain_call(client):
    print("DEMO A: a plain call")
    messages = [
        {"role": "system", "content": "You are a concise assistant for a course on AI agents."},
        {"role": "user", "content": "In one sentence, what does an AI agent do?"},
    ]
    response = client.chat(messages)
    print(f"  Model said: {response.text}")
    print(
        f"  Usage (simulated): {response.prompt_tokens} prompt tokens, "
        f"{response.completion_tokens} completion tokens"
    )
    print()


def demo_structured_call(client):
    print("DEMO B: structured output you can build on")
    messages = [
        {
            "role": "system",
            "content": (
                "You extract lead details from enquiries. FORMAT: JSON "
                "with keys name, company, need, urgency. Reply with "
                "JSON only."
            ),
        },
        {"role": "user", "content": ENQUIRY},
    ]
    response = client.chat(messages)
    print(f"  Raw reply: {response.text}")

    lead = json.loads(response.text)  # fails loudly if the model disobeys
    required = ["name", "company", "need", "urgency"]
    missing = [key for key in required if key not in lead]
    if missing:
        raise SystemExit(f"Validation failed, missing keys: {missing}")
    if lead["urgency"] not in ("low", "medium", "high"):
        raise SystemExit(f"Validation failed, bad urgency: {lead['urgency']}")
    print(f"  Parsed lead: {lead}")
    print("  Validation: OK (all required keys present, urgency is valid)")
    print(
        f"  Usage (simulated): {response.prompt_tokens} prompt tokens, "
        f"{response.completion_tokens} completion tokens"
    )


def main():
    print("Lesson 04 - Your first model call (offline, fake client)")
    print("========================================================")
    print()
    client = FakeModelClient()
    demo_plain_call(client)
    demo_structured_call(client)


if __name__ == "__main__":
    main()
