"""Lesson 11 demo: planning and reasoning patterns.

Three patterns, one scripted fake model (deterministic, clearly labelled),
real tool functions underneath:

  1. ReAct            think, act, observe, repeat until answered
  2. Plan-and-execute write the whole plan first, then run it in order
  3. Reflection       draft, critique against a checklist, revise

Same business world as the earlier lessons: BrightSmile Dental.

Fully offline, standard library only.

Run:  python3 planning_patterns.py
"""

PRICES = {"teeth whitening": 299, "emergency repair": 150, "routine checkup": 80}
CALENDAR = {"friday": ["09:00", "14:00"], "saturday": ["10:00"]}


def price_lookup(service: str) -> str:
    price = PRICES.get(service.lower())
    return f"{service}: GBP {price}" if price else f"{service}: not in the price list"


def calendar_lookup(day: str) -> str:
    slots = CALENDAR.get(day.lower(), [])
    return f"{day}: free slots {slots}" if slots else f"{day}: fully booked"


TOOLS = {"price_lookup": price_lookup, "calendar_lookup": calendar_lookup}


# ------------------------------------------------------------- 1. ReAct
def react(question: str) -> None:
    print("=== 1. ReAct: reason and act, one step at a time ===")
    print(f"question: {question}")
    trace = [
        ("I need the whitening price and the Friday calendar. Prices first.",
         "price_lookup", {"service": "teeth whitening"}),
        ("Got the price. Now check Friday availability.",
         "calendar_lookup", {"day": "friday"}),
    ]
    observations = []
    for thought, tool, args in trace:
        print(f"  Thought:     {thought}")
        print(f"  Action:      {tool}({args})")
        observation = TOOLS[tool](**args)
        observations.append(observation)
        print(f"  Observation: {observation}")
    print("  Final answer: Teeth whitening is GBP 299, and Friday has free")
    print("                slots at 09:00 and 14:00 if you want to book.")


# --------------------------------------------------- 2. Plan-and-execute
def plan_and_execute(goal: str) -> None:
    print("\n=== 2. Plan-and-execute: the whole plan before any action ===")
    print(f"goal: {goal}")
    plan = [
        ("price_lookup", {"service": "emergency repair"}),
        ("calendar_lookup", {"day": "saturday"}),
    ]
    print("  plan written up front:")
    for index, (tool, args) in enumerate(plan, start=1):
        print(f"    step {index}: {tool}({args})")
    results = []
    for index, (tool, args) in enumerate(plan, start=1):
        result = TOOLS[tool](**args)
        results.append(result)
        print(f"  executing step {index}: -> {result}")
    print("  summary: Emergency repair is GBP 150 and Saturday 10:00 is free,")
    print("           so the patient can be offered that slot.")


# --------------------------------------------------------- 3. Reflection
CHECKS = [
    ("names a specific free slot", lambda draft: "14:00" in draft),
    ("states the price", lambda draft: "299" in draft),
    ("under 60 words", lambda draft: len(draft.split()) < 60),
]


def reflection() -> None:
    print("\n=== 3. Reflection: draft, critique, revise ===")
    draft = (
        "Hi Ayesha, thanks for your message. We would love to help with "
        "whitening some time soon, just let us know what works for you."
    )
    print(f"  draft:    {draft}")
    failures = [name for name, check in CHECKS if not check(draft)]
    for name, check in CHECKS:
        print(f"  check:    {name:<28} {'PASS' if check(draft) else 'FAIL'}")
    print(f"  critique: the draft fails {len(failures)} checks: {', '.join(failures)}.")
    revised = (
        "Hi Ayesha, teeth whitening is GBP 299 for a 60 minute session. "
        "Friday 14:00 is free if you would like it. Reply to confirm."
    )
    print(f"  revised:  {revised}")
    passed = all(check(revised) for _, check in CHECKS)
    print(f"  re-check: all checks pass: {passed}")


if __name__ == "__main__":
    react("What does teeth whitening cost, and is Friday open?")
    plan_and_execute("Quote an emergency repair and find a Saturday slot.")
    reflection()
