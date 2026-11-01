"""
Lesson 03 - Exercise solution: price a conversation in tokens.

Agents rarely send one prompt. They send a growing conversation:
system instructions, the history so far, tool results, and the new
message. This script counts the tokens per message, totals them, and
warns when the conversation outgrows a given context window, which is
the moment a real agent starts silently losing its oldest context.

Run it with:

    python3 conversation_cost.py
"""

import re

TOKEN_PATTERN = re.compile(r"[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]")


def tokenize(text):
    return TOKEN_PATTERN.findall(text)


def conversation_cost(messages, window):
    """Print per-message token counts and a total against the window."""
    print(f"Context window budget: {window} tokens\n")
    total = 0
    for role, text in messages:
        count = len(tokenize(text))
        total += count
        print(f"  {role:<9} {count:>3} tokens - {text[:52]}...")
    print(f"\n  Total: {total} tokens")
    if total <= window:
        print(f"  Fits: {window - total} tokens of headroom left.")
    else:
        print(
            f"  WARNING: over budget by {total - window} tokens. "
            "The oldest messages will be dropped or must be summarised."
        )
    return total


MESSAGES = [
    ("system", "You are the front desk agent for Bright Smiles Dental. "
               "Be brief, be accurate, and never invent appointment times."),
    ("user", "Hi, do you have anything free on Saturday morning?"),
    ("agent", "Yes. Free slots on Saturday: 10:00, 12:30, 15:00. "
              "Which one would you like?"),
    ("user", "The 10:00 slot works. Please book it for me."),
    ("tool", "Booking confirmed: cleaning, Saturday 10:00, "
             "reference BK-1001, patient Dana Patel."),
    ("user", "Thanks. And can you remind me the day before?"),
]


def main():
    print("Lesson 03 - Exercise solution: conversation cost")
    print("=================================================")
    conversation_cost(MESSAGES, window=120)
    print()
    conversation_cost(MESSAGES, window=90)


if __name__ == "__main__":
    main()
